import streamlit as st
import requests
from data_utils import load_data

st.set_page_config(page_title="Traceability & Risk", layout="wide")

st.title("🔎 Traceability & Backend Risk Scoring")

df = load_data()
df.columns = df.columns.str.strip().str.lower()

API_URL = "https://smartfresh-insalata-dashboard.onrender.com/risk-score"

selected_batch = st.selectbox(
    "Select Batch ID",
    df["batch_id"].dropna().unique()
)

batch_info = df[df["batch_id"] == selected_batch]

st.subheader("📦 Batch Record")
st.dataframe(batch_info, use_container_width=True)

if len(batch_info) > 0:
    row = batch_info.iloc[0]

    st.subheader("Batch Details")

    c1, c2, c3 = st.columns(3)
    c1.metric("Product", row["product_name"])
    c2.metric("Supplier", row["supplier"])
    c3.metric("Client", row.get("client", row.get("customer", "N/A")))

    c4, c5, c6 = st.columns(3)
    c4.metric("Expiry Date", str(row["expiry_date"].date()))
    c5.metric("Delivery Status", row["delivery_status"])
    c6.metric("Temperature", f"{row['temperature']}°C")

    st.markdown("---")

    st.subheader("⚠️ Backend Risk Analyzer")

    payload = {
        "product_name": str(row["product_name"]),
        "supplier": str(row["supplier"]),
        "quantity_produced": float(row["quantity_produced"]),
        "quantity_sold": float(row["quantity_sold"]),
        "stock_remaining": float(row["stock_remaining"]),
        "waste_quantity": float(row["waste_quantity"]),
        "defect_count": int(row["defect_count"]),
        "temperature": float(row["temperature"]),
        "delivery_status": str(row["delivery_status"]),
        "delivery_delay_days": int(row["delivery_delay_days"])
    }

    if st.button("🔍 Analyze Batch Risk"):
        try:
            response = requests.post(API_URL, json=payload, timeout=15)

            if response.status_code == 200:
                result = response.json()

                r1, r2 = st.columns(2)
                r1.metric("Risk Score", result["risk_score"])
                r2.metric("Risk Category", result["risk_category"])

                st.markdown("### Risk Reasons")
                for reason in result["risk_reasons"]:
                    st.write(f"- ⚠️ {reason}")
            else:
                st.error("Backend API request failed.")
                st.write(response.text)

        except Exception as e:
            st.error("⚠️ Backend unavailable or sleeping. Try again in a few seconds.")
            st.caption(str(e))

    st.markdown("---")

    st.subheader("🧭 Traceability Summary")

    st.info(f"""
    **Batch {selected_batch}** contains **{row['product_name']}** supplied by **{row['supplier']}**
    for **{row.get('client', row.get('customer', 'N/A'))}**.

    - Produced quantity: **{row['quantity_produced']}**
    - Sold quantity: **{row['quantity_sold']}**
    - Stock remaining: **{row['stock_remaining']}**
    - Waste quantity: **{row['waste_quantity']}**
    - Defects: **{row['defect_count']}**
    - Delivery status: **{row['delivery_status']}**
    """)
