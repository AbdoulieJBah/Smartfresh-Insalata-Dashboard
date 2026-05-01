import streamlit as st
import pandas as pd
import requests
import json
import random
import time

from auth_utils import require_role
require_role(["Admin", "Manager", "Operations", "Quality", "Logistics"])

from data_utils import load_data
from ai_utils import generate_ai_response
from database import (
    save_agent_action,
    save_alert_and_action,
    save_agent_log,
    load_alerts,
    save_stream_event,
    load_stream_events,
    calculate_priority,
    assign_team
)

from notifications import notify_critical_alert
from ml_risk_model import train_risk_model, predict_ml_risk
from multi_agent import multi_agent_decision


st.set_page_config(page_title="AI Production Agent", layout="wide")

st.title("🧠 SmartFresh AI Production Agent")

st.write(
    "Autonomous AI agent for risk detection, backend risk scoring, ML-based risk prediction, "
    "multi-agent planning, auto-execution, Slack/email notifications, and real-time streaming simulation."
)

# -----------------------------
# CONTROL MODES
# -----------------------------
c1, c2, c3 = st.columns(3)

with c1:
    auto_mode = st.toggle("⚙️ Auto Monitoring", value=True)

with c2:
    autonomous_mode = st.toggle("🤖 Autonomous Actions", value=True)

with c3:
    streaming_mode = st.toggle("📡 Real-Time Streaming", value=True)

st.caption(
    "Auto Monitoring saves alerts. Autonomous Actions convert alerts into tasks and execute critical decisions. "
    "Real-Time Streaming simulates Kafka-style operational events."
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

API_URL = "https://smartfresh-api.onrender.com/risk-score"

# 🔥 TEST SLACK / EMAIL ALERT BUTTON
if st.button("🚨 Send Test Alert to Slack"):
    test_alert = {
        "risk_type": "TEST ALERT",
        "batch_id": "TEST123",
        "severity": "High",
        "priority_score": 100,
        "assigned_team": "Operations Team",
        "issue": "Testing Slack integration",
        "recommended_action": "No action"
    }

    save_alert_and_action(
        test_alert,
        status="Open",
        autonomous_mode=True
    )

    notify_result = notify_critical_alert(test_alert)

    save_agent_log(
        "TEST_NOTIFICATION",
        f"Test notification result: {notify_result}"
    )

    st.write(notify_result)
    st.success("Test alert triggered.")

# -----------------------------
# TRAIN ML RISK MODEL
# -----------------------------
ml_model, ml_features = train_risk_model(df)


# -----------------------------
# RISK DETECTION
# -----------------------------
def detect_agent_risks(data):
    alerts = []

    for _, row in data.iterrows():
        batch = row.get("batch_id", "Unknown")
        client = row.get("client", row.get("customer", "Unknown"))
        product = row.get("product_name", "Unknown")

        quantity_produced = row.get("quantity_produced", 0)
        waste_quantity = row.get("waste_quantity", 0)
        defect_count = row.get("defect_count", 0)
        temperature = row.get("temperature", 0)

        waste_rate = (waste_quantity / quantity_produced) * 100 if quantity_produced else 0

        if waste_rate > 8:
            alerts.append({
                "risk_type": "High Waste",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": f"Waste rate is {waste_rate:.2f}%",
                "recommended_action": "Review raw material quality, supplier performance, and machine settings."
            })

        if temperature > 6:
            alerts.append({
                "risk_type": "Cold Chain Risk",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": f"Temperature is {temperature:.1f}°C",
                "recommended_action": "Inspect cold storage, transport conditions, and shipment readiness."
            })

        if str(row.get("delivery_status", "")).lower() == "delayed":
            alerts.append({
                "risk_type": "Delivery Delay",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "Medium",
                "issue": "Delivery is delayed",
                "recommended_action": "Notify logistics team and review dispatch priority."
            })

        if defect_count > 25:
            alerts.append({
                "risk_type": "Quality Defect",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": f"Defect count is {defect_count}",
                "recommended_action": "Trigger quality inspection and supplier root-cause analysis."
            })

        if "slack_minutes" in data.columns and row.get("slack_minutes", 999) < 60:
            alerts.append({
                "risk_type": "Schedule Risk",
                "batch_id": batch,
                "client": client,
                "product": product,
                "severity": "High",
                "issue": "Order has less than 60 minutes slack before departure",
                "recommended_action": "Prioritize the order or reassign it to a faster machine."
            })

    alerts_df = pd.DataFrame(alerts)

    if not alerts_df.empty:
        alerts_df["priority_score"] = alerts_df.apply(
            lambda x: calculate_priority(x.to_dict()),
            axis=1
        )

        alerts_df["assigned_team"] = alerts_df.apply(
            lambda x: assign_team(x.to_dict()),
            axis=1
        )

        decisions = alerts_df.apply(
            lambda x: multi_agent_decision(x.to_dict()),
            axis=1
        )

        alerts_df["planner_recommendation"] = decisions.apply(
            lambda x: x["planner_recommendation"]
        )
        alerts_df["execute"] = decisions.apply(lambda x: x["execute"])
        alerts_df["execution_action"] = decisions.apply(lambda x: x["execution_action"])
        alerts_df["execution_status"] = decisions.apply(lambda x: x["execution_status"])

        alerts_df = alerts_df.sort_values("priority_score", ascending=False)

    return alerts_df


# -----------------------------
# REVENUE DROP DETECTION
# -----------------------------
def detect_revenue_drop(data):
    date_col = "date" if "date" in data.columns else "order_date"

    if date_col not in data.columns or "revenue" not in data.columns:
        return None, None

    rev_df = data.copy()
    rev_df[date_col] = pd.to_datetime(rev_df[date_col], errors="coerce")
    rev_df = rev_df.dropna(subset=[date_col])

    required_cols = [
        "batch_id",
        "quantity_sold",
        "waste_quantity",
        "defect_count",
        "delivery_status",
        "temperature"
    ]

    for col in required_cols:
        if col not in rev_df.columns:
            rev_df[col] = "Unknown" if col == "delivery_status" else 0

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
        return {
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
        }, daily_revenue

    return None, daily_revenue


# -----------------------------
# FUTURE REVENUE RISK
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

    if risk_percent >= 10:
        operational_risk_score += 30
        risk_reasons.append("Short-term revenue trend is below the 7-day average")

    if recent["delayed_deliveries"].mean() > 0:
        operational_risk_score += 20
        risk_reasons.append("Recent delayed deliveries detected")

    if recent["waste"].mean() > revenue_df["waste"].mean():
        operational_risk_score += 20
        risk_reasons.append("Recent waste is above normal level")

    if recent["defects"].mean() > revenue_df["defects"].mean():
        operational_risk_score += 20
        risk_reasons.append("Recent defects are above normal level")

    if recent["avg_temperature"].mean() > 6:
        operational_risk_score += 10
        risk_reasons.append("Recent average temperature is above safe threshold")

    operational_risk_score = min(operational_risk_score, 100)

    if operational_risk_score >= 70:
        risk_level = "High"
    elif operational_risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    latest_date_value = revenue_df.iloc[-1, 0]

    return {
        "latest_date": str(latest_date_value.date()) if hasattr(latest_date_value, "date") else str(latest_date_value),
        "rolling_3_day_revenue": round(short_term, 2),
        "rolling_7_day_revenue": round(normal_level, 2),
        "predicted_revenue_drop_risk_percent": round(risk_percent, 2),
        "future_revenue_risk_score": operational_risk_score,
        "future_revenue_risk_level": risk_level,
        "risk_reasons": risk_reasons if risk_reasons else ["No strong future revenue drop signal detected"]
    }


# -----------------------------
# STREAM EVENT SIMULATION
# -----------------------------
def simulate_stream_event(data):
    if data.empty:
        return None

    row = data.sample(1).iloc[0]

    event_type = random.choice([
        "Temperature Update",
        "Delivery Status Update",
        "Production Signal",
        "Quality Signal",
        "Inventory Signal"
    ])

    batch_id = row.get("batch_id", "Unknown")
    product = row.get("product_name", "Unknown")
    client = row.get("client", row.get("customer", "Unknown"))

    severity = "Info"
    message = f"{event_type} received for batch {batch_id}"

    if event_type == "Temperature Update" and row.get("temperature", 0) > 6:
        severity = "High"
        message = f"Temperature risk detected for {product}, batch {batch_id}"

    elif event_type == "Delivery Status Update" and str(row.get("delivery_status", "")).lower() == "delayed":
        severity = "Medium"
        message = f"Delayed delivery detected for client {client}, batch {batch_id}"

    elif event_type == "Quality Signal" and row.get("defect_count", 0) > 25:
        severity = "High"
        message = f"Quality defect signal detected for batch {batch_id}"

    payload = json.dumps({
        "batch_id": str(batch_id),
        "product": str(product),
        "client": str(client),
        "event_type": event_type
    })

    save_stream_event(event_type, str(batch_id), severity, message, payload)

    return {
        "event_type": event_type,
        "batch_id": batch_id,
        "severity": severity,
        "message": message
    }


# -----------------------------
# RUN DETECTION
# -----------------------------
alerts_df = detect_agent_risks(df)
revenue_alert, daily_revenue = detect_revenue_drop(df)
future_revenue_risk = predict_future_revenue_drop(daily_revenue)


# -----------------------------
# SAVE ALERTS + AUTO ACTIONS + NOTIFICATIONS
# -----------------------------
if "alerts_saved" not in st.session_state:
    st.session_state.alerts_saved = False

if auto_mode and not st.session_state.alerts_saved:
    if len(alerts_df) > 0:
        for _, alert in alerts_df.head(50).iterrows():
            alert_dict = alert.to_dict()

            save_alert_and_action(
                alert_dict,
                status="Open",
                autonomous_mode=autonomous_mode
            )

            if autonomous_mode and alert_dict.get("execute"):
                save_agent_log(
                    "AUTO_EXECUTION",
                    f"{alert_dict.get('execution_action')} executed for batch {alert_dict.get('batch_id')}"
                )

            if alert_dict.get("priority_score", 0) >= 80:
                notify_result = notify_critical_alert(alert_dict)
                save_agent_log(
                    "NOTIFICATION",
                    f"Notification result: {notify_result}"
                )

        save_agent_log(
            "Alert Save",
            f"{min(len(alerts_df), 50)} operational alerts saved. Autonomous actions: {autonomous_mode}."
        )

    if revenue_alert:
        revenue_dict = {
            "risk_type": "Revenue Drop",
            "batch_id": "N/A",
            "client": "Management",
            "product": "Revenue",
            "severity": "High",
            "issue": f"Revenue dropped by {revenue_alert['drop_percent']}%",
            "recommended_action": "Review client orders, product mix, waste, defects, and delivery delays."
        }

        revenue_dict["priority_score"] = calculate_priority(revenue_dict)
        revenue_dict["assigned_team"] = assign_team(revenue_dict)

        decision = multi_agent_decision(revenue_dict)
        revenue_dict.update(decision)

        save_alert_and_action(
            revenue_dict,
            status="Open",
            autonomous_mode=autonomous_mode
        )

        if revenue_dict.get("priority_score", 0) >= 80:
            notify_result = notify_critical_alert(revenue_dict)
            save_agent_log("NOTIFICATION", f"Revenue notification result: {notify_result}")

        save_agent_log(
            "Revenue Alert",
            f"Revenue drop detected and saved: {revenue_alert['drop_percent']}%"
        )

    if future_revenue_risk and future_revenue_risk["future_revenue_risk_level"] in ["High", "Medium"]:
        future_dict = {
            "risk_type": "Future Revenue Risk",
            "batch_id": "N/A",
            "client": "Management",
            "product": "Revenue Forecast",
            "severity": future_revenue_risk["future_revenue_risk_level"],
            "issue": f"Future revenue drop risk is {future_revenue_risk['future_revenue_risk_level']}",
            "recommended_action": "Prioritize high-value orders and reduce waste, defects, delays, and operational bottlenecks."
        }

        future_dict["priority_score"] = calculate_priority(future_dict)
        future_dict["assigned_team"] = assign_team(future_dict)

        decision = multi_agent_decision(future_dict)
        future_dict.update(decision)

        save_alert_and_action(
            future_dict,
            status="Open",
            autonomous_mode=autonomous_mode
        )

        save_agent_log(
            "Future Revenue Risk",
            f"Future revenue risk saved: {future_revenue_risk['future_revenue_risk_level']}"
        )

    st.session_state.alerts_saved = True


# -----------------------------
# REAL-TIME STREAMING CONTROL
# -----------------------------
st.markdown("---")
st.subheader("📡 Real-Time Streaming Control")

stream_col1, stream_col2, stream_col3 = st.columns(3)

with stream_col1:
    stream_auto_run = st.toggle("Live Stream Auto-Run", value=False)

with stream_col2:
    events_per_cycle = st.slider("Events per Cycle", 1, 5, 2)

with stream_col3:
    refresh_seconds = st.slider("Refresh Seconds", 3, 15, 5)

if "streaming_active" not in st.session_state:
    st.session_state.streaming_active = False

start_col, stop_col = st.columns(2)

with start_col:
    if st.button("▶️ Start Streaming"):
        st.session_state.streaming_active = True
        st.success("Live streaming started.")

with stop_col:
    if st.button("⏹️ Stop Streaming"):
        st.session_state.streaming_active = False
        st.warning("Live streaming stopped.")

if streaming_mode and (stream_auto_run or st.session_state.streaming_active):
    latest_events = []

    for _ in range(events_per_cycle):
        event = simulate_stream_event(df)
        if event:
            latest_events.append(event)

    for event in latest_events:
        if event["severity"] == "High":
            st.error(f"🚨 {event['message']}")
        elif event["severity"] == "Medium":
            st.warning(f"⚠️ {event['message']}")
        else:
            st.info(f"ℹ️ {event['message']}")

    time.sleep(refresh_seconds)
    st.rerun()

if streaming_mode:
    if st.button("📡 Simulate Single Live Event"):
        event = simulate_stream_event(df)

        if event:
            if event["severity"] == "High":
                st.error(f"🚨 {event['message']}")
            elif event["severity"] == "Medium":
                st.warning(f"⚠️ {event['message']}")
            else:
                st.info(f"ℹ️ {event['message']}")


# -----------------------------
# KPIs
# -----------------------------
st.markdown("---")
st.subheader("📌 Agent KPIs")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Records Monitored", len(df))
k2.metric("Agent Alerts", len(alerts_df))
k3.metric("High Severity", (alerts_df["severity"] == "High").sum() if len(alerts_df) else 0)
k4.metric("Autonomous Mode", "ON" if autonomous_mode else "OFF")
k5.metric("ML Model", "Active" if ml_model is not None else "Unavailable")

if st.button("🔄 Save Latest Alerts Again"):
    st.session_state.alerts_saved = False
    st.rerun()


# -----------------------------
# REVENUE DROP MONITOR
# -----------------------------
st.markdown("---")
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


# -----------------------------
# FUTURE REVENUE RISK
# -----------------------------
st.markdown("---")
st.subheader("🔮 Future Revenue Drop Prediction")

if future_revenue_risk:
    p1, p2, p3, p4 = st.columns(4)

    p1.metric("3-Day Avg Revenue", f"€{future_revenue_risk['rolling_3_day_revenue']:,.2f}")
    p2.metric("7-Day Avg Revenue", f"€{future_revenue_risk['rolling_7_day_revenue']:,.2f}")
    p3.metric("Drop Risk %", f"{future_revenue_risk['predicted_revenue_drop_risk_percent']:.2f}%")
    p4.metric("Risk Level", future_revenue_risk["future_revenue_risk_level"])

    for reason in future_revenue_risk["risk_reasons"]:
        st.write(f"- {reason}")
else:
    st.info("Not enough revenue history to predict future revenue drop.")


# -----------------------------
# AGENT ALERTS
# -----------------------------
st.markdown("---")
st.subheader("🚨 Agent Risk Alerts")

if len(alerts_df) > 0:
    display_cols = [
        "risk_type",
        "batch_id",
        "severity",
        "priority_score",
        "assigned_team",
        "planner_recommendation",
        "execution_action",
        "execution_status"
    ]

    available_cols = [col for col in display_cols if col in alerts_df.columns]

    st.dataframe(
        alerts_df[available_cols],
        use_container_width=True
    )

    st.markdown("### ⚙️ Manual Action Creation")

    for i, alert in alerts_df.head(25).iterrows():
        with st.expander(
            f"{alert['risk_type']} — Batch {alert['batch_id']} — Priority {alert['priority_score']}"
        ):
            st.write(f"**Issue:** {alert['issue']}")
            st.write(f"**Recommended Action:** {alert['recommended_action']}")
            st.write(f"**Planner Recommendation:** {alert.get('planner_recommendation', 'N/A')}")
            st.write(f"**Execution Action:** {alert.get('execution_action', 'N/A')}")
            st.write(f"**Suggested Team:** {alert['assigned_team']}")

            team_options = [
                "Operations Team",
                "Quality Team",
                "Logistics Team",
                "Management Team"
            ]

            default_index = (
                team_options.index(alert["assigned_team"])
                if alert["assigned_team"] in team_options
                else 0
            )

            team = st.selectbox(
                f"Assign Team {i}",
                team_options,
                index=default_index,
                key=f"team_{i}"
            )

            if st.button(f"Create Action {i}", key=f"create_action_{i}"):
                save_agent_action(alert.to_dict(), assigned_team=team)
                st.success("✅ Action saved to system")
else:
    st.success("✅ No major operational risks detected.")


# -----------------------------
# BACKEND RISK ANALYSIS + ML RISK
# -----------------------------
st.markdown("---")
st.subheader("🔎 Batch Traceability, Backend Risk & ML Risk Analysis")

if "batch_id" in df.columns:
    selected_batch = st.selectbox(
        "Select Batch ID",
        df["batch_id"].dropna().unique()
    )

    batch_info = df[df["batch_id"] == selected_batch]

    if len(batch_info) > 0:
        row = batch_info.iloc[0]

        b1, b2, b3 = st.columns(3)
        b1.metric("Product", row.get("product_name", "N/A"))
        b2.metric("Supplier", row.get("supplier", "N/A"))
        b3.metric("Client", row.get("client", row.get("customer", "N/A")))

        b4, b5, b6 = st.columns(3)
        b4.metric("Delivery Status", row.get("delivery_status", "N/A"))
        b5.metric("Temperature", f"{float(row.get('temperature', 0)):.1f}°C")
        b6.metric("Defects", row.get("defect_count", 0))

        payload = {
            "product_name": str(row.get("product_name", "")),
            "supplier": str(row.get("supplier", "")),
            "quantity_produced": float(row.get("quantity_produced", 0)),
            "quantity_sold": float(row.get("quantity_sold", 0)),
            "stock_remaining": float(row.get("stock_remaining", 0)),
            "waste_quantity": float(row.get("waste_quantity", 0)),
            "defect_count": int(row.get("defect_count", 0)),
            "temperature": float(row.get("temperature", 0)),
            "delivery_status": str(row.get("delivery_status", "")),
            "delivery_delay_days": int(row.get("delivery_delay_days", 0))
        }

        if st.button("🔍 Analyze Batch Risk"):
            try:
                with st.spinner("Calling SmartFresh FastAPI backend..."):
                    response = requests.post(API_URL, json=payload, timeout=30)

                if response.status_code == 200:
                    result = response.json()

                    r1, r2 = st.columns(2)
                    r1.metric("Backend Risk Score", result.get("risk_score", "N/A"))
                    r2.metric("Backend Risk Category", result.get("risk_category", "N/A"))

                    for reason in result.get("risk_reasons", []):
                        st.warning(f"⚠️ {reason}")

                    st.success("✅ Backend API connected successfully.")

                else:
                    st.error(f"Backend API failed with status code: {response.status_code}")
                    st.write(response.text)

            except requests.exceptions.Timeout:
                st.error("⚠️ Backend API timeout. Render free service may be waking up. Try again in 30 seconds.")

            except Exception as e:
                st.error("⚠️ Backend unavailable.")
                st.write(str(e))

            ml_result = predict_ml_risk(ml_model, ml_features, row)

            m1, m2 = st.columns(2)
            m1.metric("ML Risk Probability", f"{ml_result['ml_risk_probability']}%")
            m2.metric("ML Risk Level", ml_result["ml_risk_level"])

else:
    st.warning("Dataset does not contain batch_id column.")


# -----------------------------
# AI AGENT SUMMARY
# -----------------------------
st.markdown("---")
st.subheader("🧠 Agent Decision Summary")

run_agent = auto_mode or st.button("Run AI Agent Analysis")

if run_agent:
    top_alerts = alerts_df.head(20).to_dict(orient="records") if len(alerts_df) else []

    prompt = f"""
You are an autonomous AI production and business intelligence agent for a fresh produce company.

Operational risks detected:
{top_alerts}

Revenue drop alert:
{revenue_alert}

Future revenue drop prediction:
{future_revenue_risk}

System modes:
- Auto Monitoring Mode: {auto_mode}
- Autonomous Action Mode: {autonomous_mode}
- Streaming Simulation: {streaming_mode}
- ML Risk Model Active: {ml_model is not None}

Analyze:
1. Current operational health
2. Priority risks
3. Multi-agent planning recommendations
4. Executed actions
5. Revenue risk
6. What should be escalated to management

Use bullet points.
Highlight critical issues with ⚠️.
"""

    with st.spinner("AI Agent reasoning..."):
        response = generate_ai_response(prompt)
        st.markdown(response)


# -----------------------------
# STREAM FEED
# -----------------------------
st.markdown("---")
st.subheader("📡 Kafka-Style Streaming Feed")

stream_events = load_stream_events(limit=20)

if stream_events.empty:
    st.info("No streaming events yet.")
else:
    st.dataframe(stream_events, use_container_width=True)


# -----------------------------
# ALERTS FEED
# -----------------------------
st.markdown("---")
st.subheader("📡 Live Alerts Feed")

if st.button("🔄 Refresh Alerts Feed"):
    st.rerun()

saved_alerts = load_alerts()

if saved_alerts.empty:
    st.info("No alerts stored yet.")
else:
    st.dataframe(saved_alerts.head(20), use_container_width=True)
