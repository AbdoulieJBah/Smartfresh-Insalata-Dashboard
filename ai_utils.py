import streamlit as st
import google.generativeai as genai


def get_gemini_model():
    if "GEMINI_API_KEY" not in st.secrets:
        return None

    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel("gemini-1.5-flash")


def generate_ai_response(prompt):
    model = get_gemini_model()

    if model is None:
        return "⚠️ Gemini API key is missing. Add GEMINI_API_KEY in Streamlit secrets."

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI error: {e}"
