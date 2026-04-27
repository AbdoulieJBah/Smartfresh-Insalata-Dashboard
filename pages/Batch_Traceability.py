import streamlit as st
import requests
from data_utils import load_data

st.set_page_config(page_title="Batch Traceability", layout="wide")

st.title("🔎 Batch Traceability — Product Journey")

df = load_data()

selected_batch = st.selectbox(
    "Select Batch ID",
    df["batch_id"].unique()
)

batch_info = df[df["batch_id"] == selected_batch]

st.dataframe(batch_info, use_container_width=True)

if len(batch_info) > 0:
    row = batch_info.iloc[0]

    st.subheader("Batch Details")

    c1, c2, c3 = st.columns(3)
    c1.metric("Product", row["product_name"])
    c2.metric("Supplier", row["supplier"])
    c3.metric("Customer", row["customer"])

    c4, c5, c6 = st.columns(3)
    c4.metric("Expiry Date", str(row["expiry_date"].date()))
    c5.metric("Delivery Status", row["delivery_status"])
    c6.metric("Temperature", f"{row['temperature']}°C")

    if st.button("🔍 Check Backend Risk Score"):
        payload = {
            "product_name": row["product_name"],
            "supplier": row["supplier"],
            "quantity_produced": float(row["quantity_produced"]),
            "quantity_sold": float(row["quantity_sold"]),
            "stock_remaining": float(row["stock_remaining"]),
            "waste_quantity": float(row["waste_quantity"]),
            "defect_count": int(row["defect_count"]),
            "temperature": float(row["temperature"]),
            "delivery_status": row["delivery_status"],
            "delivery_delay_days": int(row["delivery_delay_days"])
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/risk-score",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                st.success(f"Risk Category: {result['risk_category']}")
                st.metric("Risk Score", result["risk_score"])

                for reason in result["risk_reasons"]:
                    st.write(f"- ⚠️ {reason}")
            else:
                st.error("Backend API request failed.")
        except Exception:
            st.warning("Backend API is not running. Run: uvicorn api:app --reload")
