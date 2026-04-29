import streamlit as st
import pandas as pd
from datetime import datetime
from data_utils import load_data
from ai_utils import generate_ai_response

st.set_page_config(page_title="AI Production Agent", layout="wide")

st.title("🧠 SmartFresh AI Production Agent")

st.write(
    "This agent monitors operations, detects risks, recommends actions, "
    "and simulates autonomous production decisions."
)

df = load_data()
df.columns = df.columns.str.strip().str.lower()

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
                "recommended_action": "Check cold storage and transport temperature control."
            })

        if str(row.get("delivery_status", "")).lower() == "delayed":
            alerts.append({
                "risk_type": "Delivery Delay",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "Medium",
                "issue": "Delivery is delayed",
                "recommended_action": "Prioritize dispatch review and notify logistics team."
            })

        if row.get("defect_count", 0) > 25:
            alerts.append({
                "risk_type": "Quality Defect",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": f"Defect count is {row.get('defect_count')}",
                "recommended_action": "Inspect packaging line and supplier quality."
            })

        if "slack_minutes" in df.columns and row.get("slack_minutes", 999) < 60:
            alerts.append({
                "risk_type": "Schedule Risk",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": "Order has less than 60 minutes slack before departure",
                "recommended_action": "Reassign to faster machine or prioritize in current shift."
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
# ALERTS
# -----------------------------
st.subheader("🚨 Agent Risk Alerts")

if len(alerts_df) > 0:
    st.dataframe(alerts_df, use_container_width=True)
else:
    st.success("✅ No major operational risks detected.")

# -----------------------------
# AGENT DECISION SUMMARY
# -----------------------------
st.subheader("🧠 Agent Decision Summary")

if st.button("Run AI Agent Analysis"):
    if len(alerts_df) == 0:
        st.success("No risks detected. Operations appear stable.")
    else:
        top_alerts = alerts_df.head(20).to_dict(orient="records")

        prompt = f"""
You are an autonomous AI production agent for a fresh produce company.

You monitor production, quality, delivery, temperature, waste, and schedule risks.

Current detected alerts:
{top_alerts}

Act like an AI agent.

Provide:
1. Overall operational status
2. Highest priority risks
3. Recommended immediate actions
4. What should be reassigned or prioritized
5. What should be escalated to management
6. Final action plan

Use clear bullet points.
Highlight critical issues with ⚠️.
"""

        with st.spinner("AI Agent is reasoning..."):
            response = generate_ai_response(prompt)
            st.markdown(response)

# -----------------------------
# SIMULATED AUTONOMOUS ACTIONS
# -----------------------------
st.subheader("⚙️ Simulated Agent Actions")

if len(alerts_df) > 0:
    for _, alert in alerts_df.head(10).iterrows():
        if alert["risk_type"] == "Schedule Risk":
            st.warning(
                f"⚠️ Agent Action: Prioritize batch {alert['batch_id']} "
                f"for faster machine assignment."
            )

        elif alert["risk_type"] == "Cold Chain Risk":
            st.error(
                f"🌡️ Agent Action: Escalate batch {alert['batch_id']} "
                f"for cold-chain inspection."
            )

        elif alert["risk_type"] == "High Waste":
            st.warning(
                f"📦 Agent Action: Review supplier/product quality for batch {alert['batch_id']}."
            )

        elif alert["risk_type"] == "Delivery Delay":
            st.info(
                f"🚚 Agent Action: Notify logistics team for client {alert['client']}."
            )

        elif alert["risk_type"] == "Quality Defect":
            st.error(
                f"🧪 Agent Action: Trigger quality inspection for batch {alert['batch_id']}."
            )
else:
    st.success("✅ No agent actions required.")
