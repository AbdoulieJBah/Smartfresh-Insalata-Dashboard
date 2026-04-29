import streamlit as st
import pandas as pd
import requests
from data_utils import load_data
from ai_utils import generate_ai_response

st.set_page_config(page_title="AI Production Agent", layout="wide")

st.title("🧠 SmartFresh AI Production Agent")

st.write(
    "This agent monitors operations, detects risks, analyzes traceability, "
    "and recommends autonomous production decisions."
)

df = load_data()
df.columns = df.columns.str.strip().str.lower()

API_URL = "https://smartfresh-insalata-dashboard.onrender.com/risk-score"

# -----------------------------
# AGENT RULES
# -----------------------------
def detect_agent_risks(df):
    alerts = []

    for _, row in df.iterrows():
        batch = row.get("batch_id", "Unknown")
        client = row.get("client", row.get("customer", "Unknown"))
        product = row.get("product_name", "Unknown")

        waste_rate = 0
        if row.get("quantity_produced", 0) > 0:
            waste_rate = (row.get("waste_quantity", 0) / row.get("quantity_produced", 1)) * 100

        if waste_rate > 8:
            alerts.append({
                "risk_type": "High Waste",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": f"Waste rate is {waste_rate:.2f}%",
                "recommended_action": "Review raw product quality, supplier, and machine settings."
            })

        if row.get("temperature", 0) > 6:
            alerts.append({
                "risk_type": "Cold Chain Risk",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": f"Temperature is {row.get('temperature')}°C",
                "recommended_action": "Check cold storage and transport."
            })

        if str(row.get("delivery_status", "")).lower() == "delayed":
            alerts.append({
                "risk_type": "Delivery Delay",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "Medium",
                "issue": "Delivery is delayed",
                "recommended_action": "Prioritize dispatch and notify logistics."
            })

        if row.get("defect_count", 0) > 25:
            alerts.append({
                "risk_type": "Quality Defect",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": f"Defect count is {row.get('defect_count')}",
                "recommended_action": "Inspect production line."
            })

        if "slack_minutes" in df.columns and row.get("slack_minutes", 999) < 60:
            alerts.append({
                "risk_type": "Schedule Risk",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": "Less than 60 minutes slack",
                "recommended_action": "Reassign to faster machine."
            })

    return pd.DataFrame(alerts)


alerts_df = detect_agent_risks(df)

# -----------------------------
# KPIs
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Records Monitored", len(df))
c2.metric("Agent Alerts", len(alerts_df))
c3.metric("High Severity", (alerts_df["severity"] == "High").sum() if len(alerts_df) else 0)
c4.metric("Medium Severity", (alerts_df["severity"] == "Medium").sum() if len(alerts_df) else 0)

st.markdown("---")

# -----------------------------
# ALERTS TABLE
# -----------------------------
st.subheader("🚨 Agent Risk Alerts")

if len(alerts_df) > 0:
    st.dataframe(alerts_df, use_container_width=True)
else:
    st.success("✅ No major operational risks detected.")

st.markdown("---")

# -----------------------------
# TRACEABILITY + BACKEND RISK
# -----------------------------
st.subheader("🔎 Batch Traceability & Risk Analysis")

selected_batch = st.selectbox(
    "Select Batch ID",
    df["batch_id"].dropna().unique()
)

batch_info = df[df["batch_id"] == selected_batch]

if len(batch_info) > 0:
    row = batch_info.iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Product", row["product_name"])
    c2.metric("Supplier", row["supplier"])
    c3.metric("Client", row.get("client", row.get("customer", "N/A")))

    c4, c5, c6 = st.columns(3)
    c4.metric("Delivery Status", row["delivery_status"])
    c5.metric("Temperature", f"{row['temperature']}°C")
    c6.metric("Defects", row["defect_count"])

    # Backend API call
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
            response = requests.post(API_URL, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()

                r1, r2 = st.columns(2)
                r1.metric("Risk Score", result["risk_score"])
                r2.metric("Risk Category", result["risk_category"])

                for reason in result["risk_reasons"]:
                    st.warning(f"⚠️ {reason}")

            else:
                st.error("Backend API failed.")

        except:
            st.error("⚠️ Backend unavailable.")

st.markdown("---")

# -----------------------------
# AI AGENT ANALYSIS
# -----------------------------
st.subheader("🧠 Agent Decision Summary")

if st.button("Run AI Agent Analysis"):
    if len(alerts_df) == 0:
        st.success("No risks detected. Operations stable.")
    else:
        top_alerts = alerts_df.head(20).to_dict(orient="records")

        prompt = f"""
You are an autonomous AI production agent.

Detected risks:
{top_alerts}

Provide:
- Operational status
- Priority risks
- Immediate actions
- What to prioritize
- Escalation plan
"""

        with st.spinner("AI Agent reasoning..."):
            response = generate_ai_response(prompt)
            st.markdown(response)

st.markdown("---")

# -----------------------------
# AUTONOMOUS ACTIONS
# -----------------------------
st.subheader("⚙️ Simulated Agent Actions")

if len(alerts_df) > 0:
    for _, alert in alerts_df.head(10).iterrows():

        if alert["risk_type"] == "Schedule Risk":
            st.warning(f"⚠️ Prioritize batch {alert['batch_id']}")

        elif alert["risk_type"] == "Cold Chain Risk":
            st.error(f"🌡️ Inspect cold chain for batch {alert['batch_id']}")

        elif alert["risk_type"] == "High Waste":
            st.warning(f"📦 Review supplier/product for batch {alert['batch_id']}")

        elif alert["risk_type"] == "Delivery Delay":
            st.info(f"🚚 Notify logistics for client {alert['client']}")

        elif alert["risk_type"] == "Quality Defect":
            st.error(f"🧪 Inspect production for batch {alert['batch_id']}")

else:
    st.success("✅ No actions required.")
