# 🛡️ Hybrid Phishing Threat Analyzer

A hybrid cybersecurity application for real-time phishing detection combining standard Machine Learning (TF-IDF + Random Forest) with Google Gemini AI.

## 🚀 Tech Stack
- Backend: FastAPI, SQLAlchemy (SQLite), Pydantic
- AI / ML: Scikit-learn (Random Forest), Google GenAI SDK (gemini-3.8-flash)
- Frontend: Streamlit
- Environment: Python 3.11+

## 📌 Features
- Dual-Engine Scoring: Combines statistical ML probability with LLM context analysis.
- Detailed Threat Insights: Extracts specific red flags and generates actionable safety advice.
- Scan Persistence: Automatically logs past analysis results to SQLite database.
- Interactive UI: Streamlit interface featuring risk meters and historical log navigation.

## 🛠️ Local Setup Instructions

1. Clone Repository:
   git clone https://github.com/abinethra/phishing-analyzer.git
   cd phishing-analyzer

2. Setup Virtual Environment:
   python -m venv backend/.venv
   .\backend\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

3. Set API Key:
   $env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

4. Run Backend Server:
   python -m uvicorn backend.main:app --reload

5. Run Frontend Interface:
   streamlit run app.py
