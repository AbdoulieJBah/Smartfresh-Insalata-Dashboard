import streamlit as st
import google.generativeai as genai
import os


def get_api_keys():
    keys = []

    # ✅ 1. Try Render environment variables FIRST
    for i in range(1, 6):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)

    # ✅ 2. Try Streamlit secrets ONLY if available
    try:
        for i in range(1, 6):
            key_name = f"GEMINI_API_KEY_{i}"
            if key_name in st.secrets:
                keys.append(st.secrets[key_name])
    except Exception:
        pass

    return keys


def generate_ai_response(prompt):
    keys = get_api_keys()

    if not keys:
        return "⚠️ No Gemini API key found. Add GEMINI_API_KEY_1 in Render Environment Variables."

    # Try each key until one works
    for key in keys:
        try:
            genai.configure(api_key=key)

            model = genai.GenerativeModel("gemini-1.5-flash")

            response = model.generate_content(prompt)

            return response.text

        except Exception as e:
            error_msg = str(e)

            # Handle quota errors → try next key
            if "429" in error_msg:
                continue

            return f"⚠️ AI error: {e}"

    # Fallback if all keys fail
    return """⚠️ AI quota reached on all keys.

Fallback insights:
- Check delayed deliveries
- Review high waste batches
- Monitor temperature deviations
- Inspect defect-heavy production lines
"""
