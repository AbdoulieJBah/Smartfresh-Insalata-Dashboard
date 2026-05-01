import os
import streamlit as st
import google.generativeai as genai


def get_api_keys():
    keys = []

    for i in range(1, 6):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)

    try:
        for i in range(1, 6):
            key_name = f"GEMINI_API_KEY_{i}"
            if key_name in st.secrets:
                keys.append(st.secrets[key_name])
    except Exception:
        pass

    return list(dict.fromkeys(keys))


@st.cache_data(ttl=120)
def generate_ai_response(prompt):
    keys = get_api_keys()

    if not keys:
        return "⚠️ No Gemini API key found in Render environment variables."

    models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-pro"
    ]

    last_error = ""

    for key in keys:
        for model_name in models:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text

            except Exception as e:
                last_error = str(e)

                if "429" in last_error or "quota" in last_error.lower():
                    continue

                if "404" in last_error or "not found" in last_error.lower():
                    continue

                continue

    return f"""⚠️ AI quota reached or all Gemini models failed.

Last error:
{last_error}

Fallback insights:
- Check delayed deliveries
- Review high-waste batches
- Monitor temperature deviations
- Inspect defect-heavy production lines
"""
