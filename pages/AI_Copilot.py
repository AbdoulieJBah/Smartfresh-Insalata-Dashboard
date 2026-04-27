import streamlit as st
from data_utils import load_data, calculate_kpis
from ai_utils import generate_ai_response

st.set_page_config(page_title="AI Copilot", layout="wide")

st.title("🤖 SmartFresh AI Copilot")

df = load_data()
kpis = calculate_kpis(df)

if "smartfresh_chat" not in st.session_state:
    st.session_state.smartfresh_chat = []

st.markdown("""
Ask questions about:
- waste
- inventory
- expiry risk
- supplier quality
- deliveries
- operational performance
""")

for msg in st.session_state.smartfresh_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask SmartFresh AI...")

if question:
    st.session_state.smartfresh_chat.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    sample_data = df.sample(min(30, len(df))).to_dict(orient="records")

    prompt = f"""
You are SmartFresh AI, an operations intelligence assistant for Insalata dell'Orto.

Analyze the fresh produce operations dataset.

Key KPIs:
- Total production: {kpis["total_production"]}
- Total sales: {kpis["total_sales"]}
- Waste rate: {kpis["waste_rate"]:.2f}%
- Defect rate: {kpis["defect_rate"]:.2f}%
- Delayed deliveries: {kpis["delayed"]}
- Total revenue: €{kpis["revenue"]:.2f}

Dataset sample:
{sample_data}

User question:
{question}

Answer clearly like a business operations analyst.
Use concise bullet points.
Highlight risks with ⚠️ where appropriate.
Give practical recommendations.
"""

    with st.chat_message("assistant"):
        with st.spinner("SmartFresh AI is analyzing..."):
            answer = generate_ai_response(prompt)
            st.markdown(answer)

    st.session_state.smartfresh_chat.append({
        "role": "assistant",
        "content": answer
    })
