import streamlit as st
import google.generativeai as genai


def get_api_keys():
    keys = []

    if "GEMINI_API_KEY_1" in st.secrets:
        keys.append(st.secrets["GEMINI_API_KEY_1"])

    if "GEMINI_API_KEY_2" in st.secrets:
        keys.append(st.secrets["GEMINI_API_KEY_2"])

    return keys


def generate_ai_response(prompt):
    keys = get_api_keys()

    if not keys:
        return "⚠️ No Gemini API keys found. Add GEMINI_API_KEY_1 and GEMINI_API_KEY_2 in Streamlit secrets."

    # Try each key until one works
    for key in keys:
        try:
            genai.configure(api_key=key)

            model = genai.GenerativeModel("gemini-2.5-flash")

            response = model.generate_content(prompt)

            return response.text

        except Exception as e:
            error_msg = str(e)

            # If quota exceeded → try next key
            if "429" in error_msg:
                continue

            # Other errors → return immediately
            return f"⚠️ AI error: {e}"

    # If all keys fail
    return """⚠️ AI quota reached on all keys.

Showing fallback insights:
- Check delayed deliveries
- Review high waste batches
- Monitor temperature deviations
- Inspect defect-heavy production lines
"""