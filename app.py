import streamlit as st
import requests

st.set_page_config(page_title="Phishing Threat Detector", page_icon="🛡️", layout="centered")

st.title("Hybrid Phishing Threat Analyzer")
st.markdown("Analyze email content, URLs, or suspicious text using **Machine Learning + Google Gemini AI**.")

# User Input Box
user_text = st.text_area("Paste suspicious text or email contents below:", height=180, placeholder="Urgent: Your account is locked...")

if st.button("Analyze Threat", type="primary", use_container_width=True):
    if not user_text.strip():
        st.warning("Please enter some text to analyze.")
    else:
        with st.spinner("Analyzing with ML model & Gemini AI..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/analyze",
                    json={"text": user_text},
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.divider()
                    
                    # Display Verdict Banner
                    verdict = data.get("verdict", "Unknown")
                    if verdict == "Phishing":
                        st.error(f"🚨 **Verdict:** {verdict}")
                    elif verdict == "Suspicious":
                        st.warning(f"⚠️ **Verdict:** {verdict}")
                    else:
                        st.success(f"✅ **Verdict:** {verdict}")
                    
                    # Display Scores
                    col1, col2 = st.columns(2)
                    risk_score = int(data.get("score", 0) * 100)
                    confidence_score = int(data.get("confidence", 0) * 100)
                    
                    col1.metric("Overall Risk Score", f"{risk_score}%")
                    col2.metric("LLM Confidence", f"{confidence_score}%")
                    
                    # Red Flags List
                    st.subheader("🚩 Red Flags Detected")
                    red_flags = data.get("red_flags", [])
                    if red_flags:
                        for flag in red_flags:
                            st.write(f"- {flag}")
                    else:
                        st.write("No explicit red flags identified.")
                    
                    # Recommendation Advice
                    st.subheader("💡 Recommendation")
                    st.info(data.get("advice", "No recommendation generated."))
                    
                else:
                    st.error(f"Server returned error code {response.status_code}. Ensure the backend is running.")
            except Exception as e:
                st.error(f"Could not connect to FastAPI backend at http://127.0.0.1:8000. Error: {e}")