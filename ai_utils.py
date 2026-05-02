import os
import streamlit as st
import google.generativeai as genai


# -----------------------------
# LOAD API KEYS
# -----------------------------
def get_api_keys():
    keys = []

    # Render environment variables
    for i in range(1, 6):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)

    # Streamlit secrets fallback
    try:
        for i in range(1, 6):
            key_name = f"GEMINI_API_KEY_{i}"
            if key_name in st.secrets:
                keys.append(st.secrets[key_name])
    except Exception:
        pass

    # Remove duplicates
    return list(dict.fromkeys(keys))


# -----------------------------
# CORE AI FUNCTION
# -----------------------------
def _generate_with_retry(prompt):
    keys = get_api_keys()

    if not keys:
        return "⚠️ No Gemini API key found."

    models = [
        "gemini-2.5-flash",
        "gemini-1.5-flash"
    ]

    last_error = ""

    for key in keys:
        for model_name in models:
            try:
                genai.configure(api_key=key)

                model = genai.GenerativeModel(model_name)

                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.4,
                        "max_output_tokens": 800
                    }
                )

                if hasattr(response, "text") and response.text:
                    return response.text

            except Exception as e:
                last_error = str(e)

                # Retry on quota or transient errors
                if "429" in last_error or "quota" in last_error.lower():
                    continue

                if "404" in last_error or "not found" in last_error.lower():
                    continue

                continue

    return f"""⚠️ AI unavailable (quota or API issue)

Last error:
{last_error}

Fallback insights:
- Check delayed deliveries
- Review high-waste batches
- Monitor temperature deviations
- Inspect defect-heavy production lines
"""


# -----------------------------
# CACHED WRAPPER (UI SAFE)
# -----------------------------
@st.cache_data(ttl=120)
def generate_ai_response_cached(prompt):
    return _generate_with_retry(prompt)


# -----------------------------
# NON-CACHED (OPTIONAL USE)
# -----------------------------
def generate_ai_response(prompt):
    return _generate_with_retry(prompt)
