import streamlit as st
import requests
from data_utils import load_data, calculate_kpis
from ai_utils import generate_ai_response

st.set_page_config(page_title="AI Copilot", layout="wide")

st.title("🤖 SmartFresh AI Copilot")

df = load_data()
kpis = calculate_kpis(df)

API_URL = "http://127.0.0.1:8000/risk-score"

# ---------------- BACKEND RISK ANALYSIS ----------------
st.subheader("🔍 Backend Risk Analyzer")

selected_batch = st.selectbox(
    "Select a batch to analyze with FastAPI backend",
    df["batch_id"].unique()
)

selected_row = df[df["batch_id"] == selected_batch].iloc[0]

if st.button("Analyze Selected Batch Risk"):
    payload = {
        "product_name": selected_row["product_name"],
        "supplier": selected_row["supplier"],
        "quantity_produced": float(selected_row["quantity_produced"]),
        "quantity_sold": float(selected_row["quantity_sold"]),
        "stock_remaining": float(selected_row["stock_remaining"]),
        "waste_quantity": float(selected_row["waste_quantity"]),
        "defect_count": int(selected_row["defect_count"]),
        "temperature": float(selected_row["temperature"]),
        "delivery_status": selected_row["delivery_status"],
        "delivery_delay_days": int(selected_row["delivery_delay_days"])
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()

            c1, c2 = st.columns(2)
            c1.metric("Backend Risk Score", result["risk_score"])
            c2.metric("Risk Category", result["risk_category"])

            st.markdown("### Risk Reasons")
            for r in result["risk_reasons"]:
                st.write(f"- ⚠️ {r}")
        else:
            st.error("Backend API request failed.")

    except Exception:
        st.warning("Backend API is not running. Start it with: python -m uvicorn api:app --reload")

st.divider()

# ---------------- AI CHAT COPILOT ----------------
st.subheader("💬 Ask SmartFresh AI")

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
