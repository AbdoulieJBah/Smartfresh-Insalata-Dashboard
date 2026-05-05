import streamlit as st
import pandas as pd
import requests
import json
import random
import time
import plotly.express as px

from auth_utils import require_role
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly
require_role(["Admin", "Manager"])

from data_utils import load_data
from ai_utils import generate_ai_response_cached
from machine_simulator import generate_machine_snapshot, summarize_machine_health

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
from ml_risk_model import train_risk_model, predict_ml_risk, get_feature_importance
from multi_agent import multi_agent_decision

setup_page("AI Production Agent")


# -----------------------------
# PREMIUM UI HELPERS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .agent-hero {
        padding: 30px;
        border-radius: 26px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.97), rgba(6,78,59,0.78)),
            radial-gradient(circle at top right, rgba(34,197,94,0.24), transparent 35%);
        border: 1px solid rgba(34,197,94,0.36);
        box-shadow: 0 18px 50px rgba(0,0,0,0.38);
        margin-bottom: 24px;
    }

    .agent-hero h1 {
        font-size: 2.25rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .agent-hero p {
        color: #d1d5db;
        font-size: 1rem;
        line-height: 1.65;
        margin: 0;
    }

    .section-title {
        font-size: 1.22rem;
        font-weight: 850;
        color: #ffffff;
        margin: 1.5rem 0 0.8rem 0;
    }

    .metric-card {
        padding: 18px;
        border-radius: 18px;
        background: rgba(15,23,42,0.88);
        border: 1px solid rgba(34,197,94,0.24);
        box-shadow: 0 12px 32px rgba(0,0,0,0.28);
        min-height: 115px;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.55rem;
        font-weight: 900;
        margin-top: 10px;
    }

    .metric-note {
        color: #86efac;
        font-size: 0.8rem;
        margin-top: 8px;
        font-weight: 650;
    }

    .insight-card {
        padding: 18px 20px;
        border-radius: 16px;
        background: rgba(15,23,42,0.82);
        border: 1px solid rgba(148,163,184,0.18);
        margin-bottom: 10px;
        color: #e5e7eb;
    }

    .insight-good { border-left: 4px solid #22c55e; }
    .insight-risk { border-left: 4px solid #f59e0b; }
    .insight-critical { border-left: 4px solid #ef4444; }

    .agent-panel {
        padding: 20px;
        border-radius: 18px;
        background: rgba(15,23,42,0.84);
        border: 1px solid rgba(34,197,94,0.22);
        box-shadow: 0 10px 28px rgba(0,0,0,0.26);
        color: #e5e7eb;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)




# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="agent-hero">
    <h1>🧠 SmartFresh AI Production Agent</h1>
    <p>
        Autonomous AI agent for operational risk detection, ML-based prediction, multi-agent planning,
        FastAPI backend scoring, Slack/email notifications, and real-time streaming simulation.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# CONTROL MODES
# -----------------------------
st.markdown('<div class="section-title">⚙️ Agent Control Modes</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    auto_mode = st.toggle("⚙️ Auto Monitoring", value=True)

with c2:
    autonomous_mode = st.toggle("🤖 Autonomous Actions", value=True)

with c3:
    streaming_mode = st.toggle("📡 Real-Time Streaming", value=True)

insight_card(
    "Auto Monitoring saves alerts. Autonomous Actions convert alerts into tasks. "
    "Real-Time Streaming simulates Kafka-style operational events."
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

API_URL = "https://smartfresh-api.onrender.com/risk-score"

# -----------------------------
# TRAIN ML RISK MODEL
# -----------------------------
ml_model, ml_features, ml_metrics = train_risk_model(df)
feature_importance_df = get_feature_importance(ml_model, ml_features)

st.markdown('<div class="section-title">🧪 ML Risk Model Status</div>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)

with m1:
    metric_card("ML Model", ml_metrics["model_type"], "Active model engine")

with m2:
    metric_card("Balanced Accuracy", ml_metrics["balanced_accuracy"], "Model stability metric")

with m3:
    metric_card("F1 Score", ml_metrics["f1_score"], "Risk detection balance")

if not feature_importance_df.empty:
    with st.expander("📊 ML Feature Importance"):
        fig_importance = px.bar(
            feature_importance_df,
            x="importance",
            y="feature",
            orientation="h",
            title="ML Feature Importance"
        )
        fig_importance = style_plotly(fig_importance)
        st.plotly_chart(fig_importance, use_container_width=True)
        st.dataframe(feature_importance_df, use_container_width=True)


# -----------------------------
# INDUSTRY 4.0 MACHINE SNAPSHOT
# -----------------------------
section_title("🏭 Industry 4.0 Machine Snapshot")

machine_df = generate_machine_snapshot()
machine_summary = summarize_machine_health(machine_df)

mc1, mc2, mc3, mc4, mc5 = st.columns(5)

with mc1:
    metric_card("Machines", machine_summary["machines"], "Connected assets")

with mc2:
    metric_card("Running", machine_summary["running"], "Active")

with mc3:
    metric_card("Warnings", machine_summary["warnings"], "Attention needed")

with mc4:
    metric_card("Stopped", machine_summary["stopped"], "Downtime risk")

with mc5:
    metric_card("Avg Risk", machine_summary["avg_risk_score"], "Machine risk")

high_machine_risk = machine_df[machine_df["risk_level"].isin(["High", "Medium"])]

if high_machine_risk.empty:
    insight_card("✅ No major simulated machine risk detected.", level="good")
else:
    for _, row in high_machine_risk.iterrows():
        level = "critical" if row["risk_level"] == "High" else "risk"
        insight_card(
            f"""
            <b>{row['machine']}</b> — {row['line']}<br>
            <b>Risk:</b> {row['risk_level']} ({row['risk_score']}/100)<br>
            <b>Reason:</b> {row['risk_reasons']}
            """,
            level=level
        )

with st.expander("📋 View Simulated Machine Feed"):
    st.dataframe(machine_df, use_container_width=True)


# -----------------------------
# RISK DETECTION
# -----------------------------
def detect_agent_risks(data, ml_model=None, ml_features=None):
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

        ml_result = {"ml_risk_probability": 0, "ml_risk_level": "Unavailable"}

        if ml_model is not None and ml_features is not None:
            ml_result = predict_ml_risk(ml_model, ml_features, row)

        ml_probability = ml_result["ml_risk_probability"]
        ml_level = ml_result["ml_risk_level"]

        base = {
            "batch_id": batch,
            "client": client,
            "product": product,
            "ml_risk_probability": ml_probability,
            "ml_risk_level": ml_level
        }

        if waste_rate > 8:
            alerts.append({
                **base,
                "risk_type": "High Waste",
                "severity": "High",
                "issue": f"Waste rate is {waste_rate:.2f}%",
                "recommended_action": "Review raw material quality, supplier performance, and machine settings."
            })

        if temperature > 6:
            alerts.append({
                **base,
                "risk_type": "Cold Chain Risk",
                "severity": "High",
                "issue": f"Temperature is {temperature:.1f}°C",
                "recommended_action": "Inspect cold storage, transport conditions, and shipment readiness."
            })

        if str(row.get("delivery_status", "")).lower() == "delayed":
            alerts.append({
                **base,
                "risk_type": "Delivery Delay",
                "severity": "Medium",
                "issue": "Delivery is delayed",
                "recommended_action": "Notify logistics team and review dispatch priority."
            })

        if defect_count > 25:
            alerts.append({
                **base,
                "risk_type": "Quality Defect",
                "severity": "High",
                "issue": f"Defect count is {defect_count}",
                "recommended_action": "Trigger quality inspection and supplier root-cause analysis."
            })

        if "slack_minutes" in data.columns and row.get("slack_minutes", 999) < 60:
            alerts.append({
                **base,
                "risk_type": "Schedule Risk",
                "severity": "High",
                "issue": "Order has less than 60 minutes slack before departure",
                "recommended_action": "Prioritize the order or reassign it to a faster machine."
            })

        if ml_probability >= 70:
            alerts.append({
                **base,
                "risk_type": "ML Predicted Risk",
                "severity": "High",
                "issue": f"ML model predicts high operational risk: {ml_probability:.2f}%",
                "recommended_action": "Investigate this batch immediately and review waste, defects, temperature, and delivery status."
            })

    alerts_df = pd.DataFrame(alerts)

    if not alerts_df.empty:
        alerts_df["priority_score"] = alerts_df.apply(
            lambda x: calculate_priority(x.to_dict()),
            axis=1
        )

        alerts_df["priority_score"] = alerts_df.apply(
            lambda x: min(100, x["priority_score"] + int(x.get("ml_risk_probability", 0) * 0.25)),
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

        alerts_df["planner_recommendation"] = decisions.apply(lambda x: x["planner_recommendation"])
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
        "batch_id", "quantity_sold", "waste_quantity",
        "defect_count", "delivery_status", "temperature"
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
alerts_df = detect_agent_risks(df, ml_model, ml_features)
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
                save_agent_log("NOTIFICATION", f"Notification result: {notify_result}")

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

        save_agent_log("Revenue Alert", f"Revenue drop detected and saved: {revenue_alert['drop_percent']}%")

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
st.markdown('<div class="section-title">📡 Real-Time Streaming Control</div>', unsafe_allow_html=True)

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
    if st.button("▶️ Start Streaming", use_container_width=True):
        st.session_state.streaming_active = True
        st.success("Live streaming started.")

with stop_col:
    if st.button("⏹️ Stop Streaming", use_container_width=True):
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
            insight_card(f"🚨 {event['message']}", level="critical")
        elif event["severity"] == "Medium":
            insight_card(f"⚠️ {event['message']}", level="risk")
        else:
            insight_card(f"ℹ️ {event['message']}")

    time.sleep(refresh_seconds)
    st.rerun()

if streaming_mode:
    if st.button("📡 Simulate Single Live Event", use_container_width=True):
        event = simulate_stream_event(df)

        if event:
            if event["severity"] == "High":
                insight_card(f"🚨 {event['message']}", level="critical")
            elif event["severity"] == "Medium":
                insight_card(f"⚠️ {event['message']}", level="risk")
            else:
                insight_card(f"ℹ️ {event['message']}")

# -----------------------------
# KPIs
# -----------------------------
st.markdown('<div class="section-title">📌 Agent KPIs</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    metric_card("Records Monitored", f"{len(df)}", "Dataset records")
with k2:
    metric_card("Agent Alerts", f"{len(alerts_df)}", "Detected risks")
with k3:
    metric_card("High Severity", f"{(alerts_df['severity'] == 'High').sum() if len(alerts_df) else 0}", "Critical risk layer")
with k4:
    metric_card("Autonomous Mode", "ON" if autonomous_mode else "OFF", "Action automation")
with k5:
    metric_card("ML Model", ml_metrics["model_type"], "Prediction engine")

if st.button("🔄 Save Latest Alerts Again", use_container_width=True):
    st.session_state.alerts_saved = False
    st.rerun()

# -----------------------------
# REVENUE DROP MONITOR
# -----------------------------
st.markdown('<div class="section-title">📉 Revenue Drop Monitor</div>', unsafe_allow_html=True)

if revenue_alert:
    insight_card(
        f"⚠️ Revenue dropped by <b>{revenue_alert['drop_percent']}%</b> on <b>{revenue_alert['date']}</b>.",
        level="critical"
    )

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        metric_card("Previous Revenue", f"€{revenue_alert['previous_revenue']:,.2f}", "Previous period")
    with r2:
        metric_card("Latest Revenue", f"€{revenue_alert['latest_revenue']:,.2f}", "Latest period")
    with r3:
        metric_card("Latest Orders", f"{revenue_alert['latest_orders']}", "Order count")
    with r4:
        metric_card("Latest Delays", f"{revenue_alert['latest_delays']}", "Logistics issue")

    causes = []
    if revenue_alert["latest_orders"] < revenue_alert["previous_orders"]:
        causes.append("Lower order volume")
    if revenue_alert["latest_quantity_sold"] < revenue_alert["previous_quantity_sold"]:
        causes.append("Lower quantity sold")
    if revenue_alert["latest_waste"] > revenue_alert["previous_waste"]:
        causes.append("Waste increased")
    if revenue_alert["latest_defects"] > revenue_alert["previous_defects"]:
        causes.append("Defects increased")
    if revenue_alert["latest_delays"] > revenue_alert["previous_delays"]:
        causes.append("Delayed deliveries increased")
    if revenue_alert["latest_avg_temperature"] > revenue_alert["previous_avg_temperature"]:
        causes.append("Temperature risk increased")

    for cause in causes:
        insight_card(f"⚠️ Possible cause: {cause}", level="risk")
else:
    insight_card("✅ No major latest-period revenue drop detected.")

# -----------------------------
# FUTURE REVENUE RISK
# -----------------------------
st.markdown('<div class="section-title">🔮 Future Revenue Drop Prediction</div>', unsafe_allow_html=True)

if future_revenue_risk:
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        metric_card("3-Day Avg Revenue", f"€{future_revenue_risk['rolling_3_day_revenue']:,.2f}", "Short-term trend")
    with p2:
        metric_card("7-Day Avg Revenue", f"€{future_revenue_risk['rolling_7_day_revenue']:,.2f}", "Normal level")
    with p3:
        metric_card("Drop Risk %", f"{future_revenue_risk['predicted_revenue_drop_risk_percent']:.2f}%", "Forecast risk")
    with p4:
        metric_card("Risk Level", future_revenue_risk["future_revenue_risk_level"], "Future revenue signal")

    for reason in future_revenue_risk["risk_reasons"]:
        insight_card(f"• {reason}", level="risk")
else:
    insight_card("Not enough revenue history to predict future revenue drop.", level="risk")

# -----------------------------
# AGENT ALERTS
# -----------------------------
st.markdown('<div class="section-title">🚨 Agent Risk Alerts</div>', unsafe_allow_html=True)

if len(alerts_df) > 0:
    display_cols = [
        "risk_type", "batch_id", "severity", "ml_risk_probability",
        "ml_risk_level", "priority_score", "assigned_team",
        "planner_recommendation", "execution_action", "execution_status"
    ]

    available_cols = [col for col in display_cols if col in alerts_df.columns]

    st.dataframe(alerts_df[available_cols], use_container_width=True)

    st.markdown('<div class="section-title">⚙️ Manual Action Creation</div>', unsafe_allow_html=True)

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
    insight_card("✅ No major operational risks detected.")

# -----------------------------
# BACKEND RISK ANALYSIS + ML RISK
# -----------------------------
st.markdown('<div class="section-title">🔎 Batch Traceability, Backend Risk & ML Risk Analysis</div>', unsafe_allow_html=True)

if "batch_id" in df.columns:
    selected_batch = st.selectbox(
        "Select Batch ID",
        df["batch_id"].dropna().unique()
    )

    batch_info = df[df["batch_id"] == selected_batch]

    if len(batch_info) > 0:
        row = batch_info.iloc[0]

        b1, b2, b3 = st.columns(3)
        with b1:
            metric_card("Product", row.get("product_name", "N/A"), "Batch product")
        with b2:
            metric_card("Supplier", row.get("supplier", "N/A"), "Source supplier")
        with b3:
            metric_card("Client", row.get("client", row.get("customer", "N/A")), "Customer")

        b4, b5, b6 = st.columns(3)
        with b4:
            metric_card("Delivery Status", row.get("delivery_status", "N/A"), "Logistics")
        with b5:
            metric_card("Temperature", f"{float(row.get('temperature', 0)):.1f}°C", "Cold-chain")
        with b6:
            metric_card("Defects", row.get("defect_count", 0), "Quality signal")

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

        if st.button("🔍 Analyze Batch Risk", use_container_width=True):
            try:
                with st.spinner("Calling SmartFresh FastAPI backend..."):
                    response = requests.post(API_URL, json=payload, timeout=30)

                if response.status_code == 200:
                    result = response.json()

                    r1, r2 = st.columns(2)
                    with r1:
                        metric_card("Backend Risk Score", result.get("risk_score", "N/A"), "FastAPI scoring")
                    with r2:
                        metric_card("Backend Risk Category", result.get("risk_category", "N/A"), "Risk class")

                    for reason in result.get("risk_reasons", []):
                        insight_card(f"⚠️ {reason}", level="risk")

                    insight_card("✅ Backend API connected successfully.")

                else:
                    insight_card(f"Backend API failed with status code: {response.status_code}", level="critical")
                    st.write(response.text)

            except requests.exceptions.Timeout:
                insight_card("⚠️ Backend API timeout. Render free service may be waking up.", level="risk")

            except Exception as e:
                insight_card("⚠️ Backend unavailable.", level="critical")
                st.write(str(e))

            ml_result = predict_ml_risk(ml_model, ml_features, row)

            m1, m2 = st.columns(2)
            with m1:
                metric_card("ML Risk Probability", f"{ml_result['ml_risk_probability']}%", "Model prediction")
            with m2:
                metric_card("ML Risk Level", ml_result["ml_risk_level"], "ML risk class")
else:
    insight_card("Dataset does not contain batch_id column.", level="risk")

# -----------------------------
# AI AGENT SUMMARY
# -----------------------------
st.markdown('<div class="section-title">🧠 Agent Decision Summary</div>', unsafe_allow_html=True)

run_agent = st.button("Run AI Agent Analysis", use_container_width=True)

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
- ML Model: {ml_metrics['model_type']}
- ML Balanced Accuracy: {ml_metrics['balanced_accuracy']}
- ML F1 Score: {ml_metrics['f1_score']}

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
        response = generate_ai_response_cached(prompt)
        st.markdown(response)

# -----------------------------
# STREAM FEED
# -----------------------------
st.markdown('<div class="section-title">📡 Kafka-Style Streaming Feed</div>', unsafe_allow_html=True)

stream_events = load_stream_events(limit=20)

if stream_events.empty:
    insight_card("No streaming events yet.", level="risk")
else:
    st.dataframe(stream_events, use_container_width=True)

# -----------------------------
# ALERTS FEED
# -----------------------------
st.markdown('<div class="section-title">📡 Live Alerts Feed</div>', unsafe_allow_html=True)

if st.button("🔄 Refresh Alerts Feed", use_container_width=True):
    st.rerun()

saved_alerts = load_alerts()

if saved_alerts.empty:
    insight_card("No alerts stored yet.", level="risk")
else:
    st.dataframe(saved_alerts.head(20), use_container_width=True)
