import time
import streamlit as st
import plotly.express as px

from auth_utils import require_role
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly
from machine_simulator import (
    generate_operator_session,
    generate_machine_snapshot,
    generate_machine_history,
    summarize_machine_health,
    generate_ai_operator_recommendation,
)

require_role(["Admin", "Manager", "Operations", "Quality", "Logistics"])

setup_page("Machine Digital Twin", icon="🏭")

premium_hero(
    "🏭 Machine Digital Twin",
    "Industry 4.0 simulation of MES operator workflow, shop-floor machine signals, anomaly detection, and AI-driven production recommendations."
)

# -----------------------------
# CONTROLS
# -----------------------------
section_title("⚙️ Digital Twin Controls")

c1, c2, c3 = st.columns(3)

with c1:
    live_mode = st.toggle("📡 Live Simulation", value=False)

with c2:
    refresh_seconds = st.slider("Refresh seconds", 2, 15, 5)

with c3:
    history_cycles = st.slider("History cycles", 10, 100, 40)

# -----------------------------
# DATA
# -----------------------------
session = generate_operator_session()
machine_df = generate_machine_snapshot()
history_df = generate_machine_history(cycles=history_cycles)
summary = summarize_machine_health(machine_df)

# -----------------------------
# MES OPERATOR PANEL
# -----------------------------
section_title("👷 MES Operator Panel")

progress = session["produced_qty"] / session["ordered_qty"]

st.markdown(f"""
<div class="glass-card" style="padding:22px; margin-bottom:18px;">
    <h3>Work Order: {session['work_order']}</h3>
    <b>Operator:</b> {session['operator']} |
    <b>Shift:</b> {session['shift']} |
    <b>Line:</b> {session['line']}<br><br>

    <b>Client:</b> {session['client']} |
    <b>Destination:</b> {session['destination']}<br>

    <b>Product:</b> {session['product']} |
    <b>Phase:</b> {session['phase']}<br><br>

    <b>Status:</b> {session['status']} |
    <b>Start Time:</b> {session['start_time']}<br>

    <b>Notes:</b> {session['notes']}
</div>
""", unsafe_allow_html=True)

q1, q2, q3, q4 = st.columns(4)

with q1:
    metric_card("Ordered Qty", f"{session['ordered_qty']:,}", "ERP demand")

with q2:
    metric_card("Produced Qty", f"{session['produced_qty']:,}", "MES output")

with q3:
    metric_card("To Produce", f"{session['to_produce']:,}", "Current target")

with q4:
    metric_card("Remaining", f"{session['remaining']:,}", "Open quantity")

st.progress(progress)

# -----------------------------
# MACHINE HEALTH
# -----------------------------
section_title("📌 Machine Health Overview")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    metric_card("Machines", summary["machines"], "Connected assets")

with k2:
    metric_card("Running", summary["running"], "Active")

with k3:
    metric_card("Warnings", summary["warnings"], "Attention needed")

with k4:
    metric_card("Stopped", summary["stopped"], "Downtime risk")

with k5:
    metric_card("High Risk", summary["high_risk"], "Critical")

with k6:
    metric_card("Avg Risk", summary["avg_risk_score"], "Risk score")

# -----------------------------
# LIVE MACHINE STATUS
# -----------------------------
section_title("🖥️ Live Machine Status")

for _, row in machine_df.iterrows():
    if row["risk_level"] == "High":
        level = "critical"
    elif row["risk_level"] == "Medium":
        level = "risk"
    else:
        level = "good"

    recommendation = generate_ai_operator_recommendation(row)

    insight_card(
        f"""
        <b>{row['machine_name']}</b> — {row['line']}<br>
        <b>Type:</b> {row['machine_type']} |
        <b>Status:</b> {row['status']} |
        <b>Product:</b> {row['product']}<br>
        <b>Risk:</b> {row['risk_level']} ({row['risk_score']}/100)<br>
        <b>Alarm:</b> {row['alarm']}<br>
        <b>Reason:</b> {row['risk_reasons']}<br>
        <b>AI Recommendation:</b> {recommendation}
        """,
        level=level
    )

# -----------------------------
# MACHINE DATA FEED
# -----------------------------
section_title("📋 Machine Data Feed")

display_cols = [
    "timestamp",
    "machine_id",
    "machine_name",
    "machine_type",
    "line",
    "product",
    "status",
    "speed",
    "target_speed",
    "temperature",
    "target_weight",
    "weight_avg",
    "accepted_packs",
    "rejected_packs",
    "reject_rate",
    "downtime_minutes",
    "vibration",
    "alarm",
    "risk_score",
    "risk_level",
]

st.dataframe(machine_df[display_cols], use_container_width=True)

# -----------------------------
# CHARTS
# -----------------------------
section_title("📊 Machine Intelligence Charts")

chart1, chart2 = st.columns(2)

with chart1:
    fig_status = px.bar(
        machine_df,
        x="machine_name",
        y="risk_score",
        color="risk_level",
        title="Current Machine Risk Score"
    )
    st.plotly_chart(style_plotly(fig_status), use_container_width=True)

with chart2:
    fig_defect = px.bar(
        machine_df,
        x="machine_name",
        y="reject_rate",
        color="status",
        title="Current Reject Rate"
    )
    st.plotly_chart(style_plotly(fig_defect), use_container_width=True)

chart3, chart4 = st.columns(2)

with chart3:
    fig_speed = px.bar(
        machine_df,
        x="machine_name",
        y=["speed", "target_speed"],
        barmode="group",
        title="Speed vs Target Speed"
    )
    st.plotly_chart(style_plotly(fig_speed), use_container_width=True)

with chart4:
    fig_weight = px.bar(
        machine_df,
        x="machine_name",
        y=["weight_avg", "target_weight"],
        barmode="group",
        title="Average Weight vs Target Weight"
    )
    st.plotly_chart(style_plotly(fig_weight), use_container_width=True)

# -----------------------------
# HISTORY ANALYTICS
# -----------------------------
section_title("📈 Simulated Machine History")

fig_history = px.line(
    history_df,
    x="timestamp",
    y="risk_score",
    color="machine_name",
    title="Machine Risk Trend Over Simulated Time"
)
st.plotly_chart(style_plotly(fig_history), use_container_width=True)

fig_temp = px.line(
    history_df,
    x="timestamp",
    y="temperature",
    color="machine_name",
    title="Temperature Trend by Machine"
)
st.plotly_chart(style_plotly(fig_temp), use_container_width=True)

# -----------------------------
# AI RECOMMENDATIONS
# -----------------------------
section_title("🤖 AI Machine Recommendations")

high_risk_df = machine_df[machine_df["risk_level"].isin(["High", "Medium"])]

if high_risk_df.empty:
    insight_card("✅ All machines are operating within acceptable simulated limits.", level="good")
else:
    for _, row in high_risk_df.iterrows():
        insight_card(
            f"""
            <b>{row['machine_name']}</b><br>
            ⚠️ Risk detected: {row['risk_reasons']}<br>
            ✅ Recommended action: {generate_ai_operator_recommendation(row)}
            """,
            level="risk"
        )

# -----------------------------
# DOWNLOAD
# -----------------------------
st.download_button(
    "Download Machine Simulation Data",
    machine_df.to_csv(index=False),
    "smartfresh_machine_simulation.csv",
    "text/csv",
    use_container_width=True
)

# -----------------------------
# LIVE REFRESH
# -----------------------------
if live_mode:
    time.sleep(refresh_seconds)
    st.rerun()
