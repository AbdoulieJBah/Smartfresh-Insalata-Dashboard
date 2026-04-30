import streamlit as st
import pandas as pd
import numpy as np
import requests
from data_utils import load_data
from ai_utils import generate_ai_response
from database import save_agent_action
from database import save_alert, save_agent_log

st.set_page_config(page_title="AI Production Agent", layout="wide")

st.title("🧠 SmartFresh AI Production Agent")

st.write(
    "This agent monitors operations, detects risks, analyzes revenue drops, predicts future revenue risk, "
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
                "issue": f"Temperature is {row.get('temperature'):.1f}°C",
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


# -----------------------------
# REVENUE DROP DETECTION
# -----------------------------
def detect_revenue_drop(df):
    date_col = "date" if "date" in df.columns else "order_date"

    if date_col not in df.columns or "revenue" not in df.columns:
        return None, None

    rev_df = df.copy()
    rev_df[date_col] = pd.to_datetime(rev_df[date_col], errors="coerce")
    rev_df = rev_df.dropna(subset=[date_col])

    daily_revenue = (
        rev_df.groupby(date_col)
        .agg(
            revenue=("revenue", "sum"),
            orders=("batch_id", "count"),
            quantity_sold=("quantity_sold", "sum"),
            waste=("waste_quantity", "sum"),
            defects=("defect_count", "sum"),
            delayed_deliveries=("delivery_status", lambda x: (x.astype(str).str.lower() == "delayed").sum()),
            avg_temperature=("temperature", "mean")
        )
        .reset_index()
        .sort_values(date_col)
    )

    if len(daily_revenue) < 2:
        return None, daily_revenue

    latest = daily_revenue.iloc[-1]
    previous = daily_revenue.iloc[-2]

    previous_revenue = previous["revenue"]
    latest_revenue = latest["revenue"]

    if previous_revenue == 0:
        return None, daily_revenue

    drop_percent = ((previous_revenue - latest_revenue) / previous_revenue) * 100

    if drop_percent >= 15:
        alert = {
            "date": str(latest[date_col].date()),
            "previous_revenue": round(previous_revenue, 2),
            "latest_revenue": round(latest_revenue, 2),
            "drop_percent": round(drop_percent, 2),
            "latest_orders": int(latest["orders"]),
            "previous_orders": int(previous["orders"]),
            "latest_quantity_sold": int(latest["quantity_sold"]),
            "previous_quantity_sold": int(previous["quantity_sold"]),
            "latest_waste": int(latest["waste"]),
            "previous_waste": int(previous["waste"]),
            "latest_defects": int(latest["defects"]),
            "previous_defects": int(previous["defects"]),
            "latest_delays": int(latest["delayed_deliveries"]),
            "previous_delays": int(previous["delayed_deliveries"]),
            "latest_avg_temperature": round(latest["avg_temperature"], 2),
            "previous_avg_temperature": round(previous["avg_temperature"], 2),
        }

        return alert, daily_revenue

    return None, daily_revenue


# -----------------------------
# FUTURE REVENUE DROP PREDICTION
# -----------------------------
def predict_future_revenue_drop(daily_revenue):
    if daily_revenue is None or len(daily_revenue) < 7:
        return None

    revenue_df = daily_revenue.copy()
    revenue_df["rolling_3_day_revenue"] = revenue_df["revenue"].rolling(window=3).mean()
    revenue_df["rolling_7_day_revenue"] = revenue_df["revenue"].rolling(window=7).mean()

    latest = revenue_df.iloc[-1]

    if pd.isna(latest["rolling_3_day_revenue"]) or pd.isna(latest["rolling_7_day_revenue"]):
        return None

    short_term = latest["rolling_3_day_revenue"]
    normal_level = latest["rolling_7_day_revenue"]

    risk_percent = ((normal_level - short_term) / normal_level) * 100 if normal_level else 0

    operational_risk_score = 0
    risk_reasons = []

    recent = revenue_df.tail(3)

    avg_waste = recent["waste"].mean()
    avg_defects = recent["defects"].mean()
    avg_delays = recent["delayed_deliveries"].mean()
    avg_temperature = recent["avg_temperature"].mean()

    if risk_percent >= 10:
        operational_risk_score += 30
        risk_reasons.append("Short-term revenue trend is below the 7-day average")

    if avg_delays > 0:
        operational_risk_score += 20
        risk_reasons.append("Recent delayed deliveries detected")

    if avg_waste > revenue_df["waste"].mean():
        operational_risk_score += 20
        risk_reasons.append("Recent waste is above normal level")

    if avg_defects > revenue_df["defects"].mean():
        operational_risk_score += 20
        risk_reasons.append("Recent defects are above normal level")

    if avg_temperature > 6:
        operational_risk_score += 10
        risk_reasons.append("Recent average temperature is above safe threshold")

    operational_risk_score = min(operational_risk_score, 100)

    if operational_risk_score >= 70:
        risk_level = "High"
    elif operational_risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "latest_date": str(latest.iloc[0].date()) if hasattr(latest.iloc[0], "date") else str(latest.iloc[0]),
        "rolling_3_day_revenue": round(short_term, 2),
        "rolling_7_day_revenue": round(normal_level, 2),
        "predicted_revenue_drop_risk_percent": round(risk_percent, 2),
        "future_revenue_risk_score": operational_risk_score,
        "future_revenue_risk_level": risk_level,
        "risk_reasons": risk_reasons if risk_reasons else ["No strong future revenue drop signal detected"]
    }


alerts_df = detect_agent_risks(df)
revenue_alert, daily_revenue = detect_revenue_drop(df)
future_revenue_risk = predict_future_revenue_drop(daily_revenue)

# -----------------------------
# SAVE ALERTS TO DATABASE
# -----------------------------
if "alerts_saved" not in st.session_state:
    st.session_state.alerts_saved = False

if not st.session_state.alerts_saved:
    if len(alerts_df) > 0:
        for _, alert in alerts_df.head(50).iterrows():
            save_alert(alert.to_dict(), status="Open")

        save_agent_log(
            "Alert Save",
            f"{min(len(alerts_df), 50)} operational alerts saved by AI Production Agent."
        )

    if revenue_alert:
        save_alert(
            {
                "risk_type": "Revenue Drop",
                "batch_id": "N/A",
                "severity": "High",
                "issue": f"Revenue dropped by {revenue_alert['drop_percent']}%",
                "recommended_action": "Review client orders, product mix, waste, defects, and delivery delays."
            },
            status="Open"
        )

        save_agent_log(
            "Revenue Alert",
            f"Revenue drop detected and saved: {revenue_alert['drop_percent']}%"
        )

    if future_revenue_risk and future_revenue_risk["future_revenue_risk_level"] in ["High", "Medium"]:
        save_alert(
            {
                "risk_type": "Future Revenue Risk",
                "batch_id": "N/A",
                "severity": future_revenue_risk["future_revenue_risk_level"],
                "issue": f"Future revenue drop risk is {future_revenue_risk['future_revenue_risk_level']}",
                "recommended_action": "Prioritize high-value orders and reduce waste, defects, delays, and operational bottlenecks."
            },
            status="Open"
        )

        save_agent_log(
            "Future Revenue Risk",
            f"Future revenue risk saved: {future_revenue_risk['future_revenue_risk_level']}"
        )

    st.session_state.alerts_saved = True

# -----------------------------
# KPIs
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Records Monitored", len(df))
c2.metric("Agent Alerts", len(alerts_df))
c3.metric("High Severity", (alerts_df["severity"] == "High").sum() if len(alerts_df) else 0)
c4.metric("Medium Severity", (alerts_df["severity"] == "Medium").sum() if len(alerts_df) else 0)

if st.button("🔄 Save Latest Alerts Again"):
    st.session_state.alerts_saved = False
    st.rerun()

st.markdown("---")

# -----------------------------
# REVENUE DROP MONITOR
# -----------------------------
st.subheader("📉 Revenue Drop Monitor")

if revenue_alert:
    st.error(
        f"⚠️ Revenue dropped by {revenue_alert['drop_percent']}% on {revenue_alert['date']}."
    )

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Previous Revenue", f"€{revenue_alert['previous_revenue']:,.2f}")
    r2.metric("Latest Revenue", f"€{revenue_alert['latest_revenue']:,.2f}")
    r3.metric("Latest Orders", revenue_alert["latest_orders"])
    r4.metric("Latest Delays", revenue_alert["latest_delays"])

    st.markdown("### Possible Causes")
    if revenue_alert["latest_orders"] < revenue_alert["previous_orders"]:
        st.write("- ⚠️ Lower order volume")
    if revenue_alert["latest_quantity_sold"] < revenue_alert["previous_quantity_sold"]:
        st.write("- ⚠️ Lower quantity sold")
    if revenue_alert["latest_waste"] > revenue_alert["previous_waste"]:
        st.write("- ⚠️ Waste increased")
    if revenue_alert["latest_defects"] > revenue_alert["previous_defects"]:
        st.write("- ⚠️ Defects increased")
    if revenue_alert["latest_delays"] > revenue_alert["previous_delays"]:
        st.write("- ⚠️ Delayed deliveries increased")
    if revenue_alert["latest_avg_temperature"] > revenue_alert["previous_avg_temperature"]:
        st.write("- ⚠️ Temperature risk increased")
else:
    st.success("✅ No major latest-period revenue drop detected.")

st.markdown("---")

# -----------------------------
# FUTURE REVENUE DROP PREDICTION
# -----------------------------
st.subheader("🔮 Future Revenue Drop Prediction")

if future_revenue_risk:
    p1, p2, p3, p4 = st.columns(4)

    p1.metric("3-Day Avg Revenue", f"€{future_revenue_risk['rolling_3_day_revenue']:,.2f}")
    p2.metric("7-Day Avg Revenue", f"€{future_revenue_risk['rolling_7_day_revenue']:,.2f}")
    p3.metric("Drop Risk %", f"{future_revenue_risk['predicted_revenue_drop_risk_percent']:.2f}%")
    p4.metric("Risk Level", future_revenue_risk["future_revenue_risk_level"])

    if future_revenue_risk["future_revenue_risk_level"] == "High":
        st.error("🔴 High future revenue drop risk detected.")
    elif future_revenue_risk["future_revenue_risk_level"] == "Medium":
        st.warning("🟡 Medium future revenue drop risk detected.")
    else:
        st.success("🟢 Low future revenue drop risk.")

    st.markdown("### Prediction Reasons")
    for reason in future_revenue_risk["risk_reasons"]:
        st.write(f"- {reason}")
else:
    st.info("Not enough revenue history to predict future revenue drop.")

st.markdown("---")

# -----------------------------
# AGENT ALERTS
# -----------------------------
st.subheader("🚨 Agent Risk Alerts")

if len(alerts_df) > 0:
    st.dataframe(alerts_df, use_container_width=True)

    st.markdown("### ⚙️ Convert Alerts to Actions")

    for i, alert in alerts_df.iterrows():
        with st.expander(f"{alert['risk_type']} — Batch {alert['batch_id']}"):

            st.write(f"**Issue:** {alert['issue']}")
            st.write(f"**Recommended Action:** {alert['recommended_action']}")

            team = st.selectbox(
                f"Assign Team {i}",
                ["Operations Team", "Quality Team", "Logistics Team"],
                key=f"team_{i}"
            )

            if st.button(f"Create Action {i}"):
                save_agent_action(alert.to_dict(), assigned_team=team)
                st.success("✅ Action saved to system")
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
    c5.metric("Temperature", f"{row['temperature']:.1f}°C")
    c6.metric("Defects", row["defect_count"])

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

        except Exception:
            st.error("⚠️ Backend unavailable.")

st.markdown("---")

# -----------------------------
# AI AGENT ANALYSIS
# -----------------------------
st.subheader("🧠 Agent Decision Summary")

if st.button("Run AI Agent Analysis"):
    top_alerts = alerts_df.head(20).to_dict(orient="records") if len(alerts_df) else []

    prompt = f"""
You are an autonomous AI production and business intelligence agent for a fresh produce company.

Operational risks detected:
{top_alerts}

Revenue drop alert:
{revenue_alert}

Future revenue drop prediction:
{future_revenue_risk}

Analyze:
1. Current operational health
2. Reasons revenue may have dropped
3. Future revenue risk
4. Priority operational risks
5. Immediate corrective actions
6. What should be escalated to management

Use clear bullet points.
Highlight critical issues with ⚠️.
"""

    with st.spinner("AI Agent reasoning..."):
        response = generate_ai_response(prompt)
        st.markdown(response)

st.markdown("---")

# -----------------------------
# SIMULATED AUTONOMOUS ACTIONS
# -----------------------------
st.subheader("⚙️ Simulated Agent Actions")

if revenue_alert:
    st.warning("💰 Agent Action: Revenue drop detected — review client orders, product mix, waste, and delayed deliveries.")

if future_revenue_risk and future_revenue_risk["future_revenue_risk_level"] in ["High", "Medium"]:
    st.warning("🔮 Agent Action: Future revenue risk detected — prioritize high-value orders and reduce operational bottlenecks.")

if len(alerts_df) > 0:
    for _, alert in alerts_df.head(10).iterrows():
        if alert["risk_type"] == "Schedule Risk":
            st.warning(f"⚠️ Prioritize batch {alert['batch_id']} for faster machine assignment.")

        elif alert["risk_type"] == "Cold Chain Risk":
            st.error(f"🌡️ Inspect cold chain for batch {alert['batch_id']}.")

        elif alert["risk_type"] == "High Waste":
            st.warning(f"📦 Review supplier/product quality for batch {alert['batch_id']}.")

        elif alert["risk_type"] == "Delivery Delay":
            st.info(f"🚚 Notify logistics for client {alert['client']}.")

        elif alert["risk_type"] == "Quality Defect":
            st.error(f"🧪 Trigger quality inspection for batch {alert['batch_id']}.")
else:
    if not revenue_alert and not future_revenue_risk:
        st.success("✅ No agent actions required.")
