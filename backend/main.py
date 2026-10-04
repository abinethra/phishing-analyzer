import os
import json
import datetime
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import joblib
from google import genai

# --- 1. Database Setup (SQLite) ---
DATABASE_URL = "sqlite:///./scans.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(String)
    ml_score = Column(Float)
    verdict = Column(String)
    explanation = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 2. Load ML Model & Vectorizer ---
vectorizer = joblib.load("tfidf_vectorizer.pkl")
clf = joblib.load("phishing_model.pkl")

# --- 3. Gemini API Setup ---
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else genai.Client()

SYS_PROMPT = """You are a cybersecurity expert analyzing potential phishing emails or URLs.
Analyze the input text and respond STRICTLY with a valid JSON object with these keys:
- "verdict": "Safe", "Suspicious", or "Phishing"
- "confidence": float value between 0.0 and 1.0
- "red_flags": list of strings detailing suspicious indicators
- "advice": string safety recommendation for user
Do not include markdown code block syntax (like ```json). Return raw JSON only."""

app = FastAPI()

class AnalyzeReq(BaseModel):
    text: str = Field(..., max_length=4000)

@app.get("/")
def read_root():
    return {"status": "Phishing Analyzer API is running"}

@app.post("/analyze")
def analyze(req: AnalyzeReq, db: Session = Depends(get_db)):
    try:
        # 1. ML Model Prediction
        vec = vectorizer.transform([req.text])
        ml = float(clf.predict_proba(vec)[0][1])

        # 2. Call Gemini API
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"{SYS_PROMPT}\n\nContent to analyze:\n{req.text[:4000]}"
        )
        
        # Clean response text if model returns markdown formatting
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        
        llm = json.loads(raw_text.strip())

        # 3. Combined Score
        final = round(0.5 * ml + 0.5 * float(llm.get("confidence", 0.5)), 2)

        # 4. Save to DB
        db_scan = Scan(
            input_text=req.text,
            ml_score=ml,
            verdict=llm.get("verdict", "Unknown"),
            explanation=str(llm.get("red_flags", []))
        )
        db.add(db_scan)
        db.commit()

        return {"score": final, **llm}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(Scan).order_by(Scan.created_at.desc()).all()