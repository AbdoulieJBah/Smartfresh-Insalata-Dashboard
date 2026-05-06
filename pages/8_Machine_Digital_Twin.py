import time
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from auth_utils import require_role
from utils import setup_page, premium_hero, metric_card, section_title, style_plotly
from machine_simulator import (
    generate_operator_session,
    generate_machine_snapshot,
    generate_machine_history,
    summarize_machine_health,
    generate_ai_operator_recommendation,
)

require_role(["Admin", "Manager", "Operations", "Quality", "Logistics"])

setup_page("Machine Digital Twin", icon="🏭")

# -----------------------------
# PAGE CSS
# -----------------------------
st.markdown("""
<style>
.status-dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}

.dot-green { background:#22c55e; box-shadow:0 0 12px #22c55e; }
.dot-yellow { background:#f59e0b; box-shadow:0 0 12px #f59e0b; }
.dot-red { background:#ef4444; box-shadow:0 0 12px #ef4444; }

@keyframes pulse {
    0% { opacity: 0.45; transform: scale(0.95); }
    50% { opacity: 1; transform: scale(1.15); }
    100% { opacity: 0.45; transform: scale(0.95); }
}

.machine-card {
    padding: 20px;
    border-radius: 20px;
    background: rgba(15,23,42,0.82);
    border: 1px solid rgba(34,197,94,0.22);
    box-shadow: 0 14px 34px rgba(0,0,0,0.30);
    margin-bottom: 16px;
    color: #e5e7eb;
}

.machine-good { border-left: 5px solid #22c55e; }
.machine-risk { border-left: 5px solid #f59e0b; }
.machine-critical { border-left: 5px solid #ef4444; }

.machine-title {
    font-size: 1.15rem;
    font-weight: 950;
    color: #ffffff;
    margin-bottom: 8px;
}

.machine-small {
    color: #9ca3af;
    font-size: 0.85rem;
    font-weight: 700;
}

.escalation-banner {
    padding: 18px 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(239,68,68,0.18), rgba(15,23,42,0.90));
    border: 1px solid rgba(239,68,68,0.45);
    box-shadow: 0 16px 40px rgba(239,68,68,0.14);
    margin-bottom: 18px;
    color: #f8fafc;
}

.operator-panel {
    padding: 24px;
    border-radius: 22px;
    background: rgba(15,23,42,0.86);
    border: 1px solid rgba(34,197,94,0.28);
    box-shadow: 0 18px 45px rgba(0,0,0,0.35);
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
premium_hero(
    "🏭 Machine Digital Twin",
    "Industry 4.0 simulation of MES operator workflow, shop-floor machine signals, anomaly detection, OEE monitoring, and AI-driven production recommendations.",
    badge="Industry 4.0 Digital Twin"
)

st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

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
# OEE CALCULATION
# -----------------------------
machine_df["availability"] = (100 - machine_df["downtime_minutes"].clip(0, 100)).clip(0, 100)
machine_df["performance"] = ((machine_df["speed"] / machine_df["target_speed"]) * 100).clip(0, 120)
machine_df["quality"] = (100 - machine_df["reject_rate"]).clip(0, 100)
machine_df["oee"] = (
    machine_df["availability"] *
    machine_df["performance"] *
    machine_df["quality"]
) / 10000

avg_oee = machine_df["oee"].mean()
avg_availability = machine_df["availability"].mean()
avg_performance = machine_df["performance"].mean()
avg_quality = machine_df["quality"].mean()

# -----------------------------
# AI ESCALATION
# -----------------------------
critical_df = machine_df[machine_df["risk_level"] == "High"]

if not critical_df.empty:
    worst = critical_df.sort_values("risk_score", ascending=False).iloc[0]
    st.markdown(f"""
    <div class="escalation-banner">
        🚨 <b>AI ESCALATION:</b> {worst['machine_name']} on {worst['line']} requires immediate attention.<br>
        <b>Risk Score:</b> {worst['risk_score']}/100<br>
        <b>Reason:</b> {worst['risk_reasons']}<br>
        <b>Recommended Action:</b> {generate_ai_operator_recommendation(worst)}
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# MES OPERATOR PANEL
# -----------------------------
section_title("👷 MES Operator Panel")

progress = session["produced_qty"] / session["ordered_qty"]

st.markdown(f"""
<div class="operator-panel">
    <div class="machine-title">Work Order: {session['work_order']}</div>
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
# OEE METRICS
# -----------------------------
section_title("🏭 OEE Performance Layer")

o1, o2, o3, o4 = st.columns(4)

with o1:
    metric_card("OEE", f"{avg_oee:.1f}%", "Overall equipment effectiveness")

with o2:
    metric_card("Availability", f"{avg_availability:.1f}%", "Downtime impact")

with o3:
    metric_card("Performance", f"{avg_performance:.1f}%", "Speed vs target")

with o4:
    metric_card("Quality", f"{avg_quality:.1f}%", "Accepted output quality")

fig_oee = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_oee,
    title={"text": "Average OEE %"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "#22c55e"},
        "steps": [
            {"range": [0, 50], "color": "rgba(239,68,68,0.25)"},
            {"range": [50, 75], "color": "rgba(245,158,11,0.25)"},
            {"range": [75, 100], "color": "rgba(34,197,94,0.25)"},
        ],
    }
))
fig_oee.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    font={"color": "#e5e7eb"},
    height=320,
)
st.plotly_chart(fig_oee, use_container_width=True)

# -----------------------------
# LIVE MACHINE STATUS
# -----------------------------
section_title("🖥️ Live Machine Status")

for _, row in machine_df.iterrows():
    if row["risk_level"] == "High":
        card_class = "machine-critical"
        dot_class = "dot-red"
    elif row["risk_level"] == "Medium":
        card_class = "machine-risk"
        dot_class = "dot-yellow"
    else:
        card_class = "machine-good"
        dot_class = "dot-green"

    recommendation = generate_ai_operator_recommendation(row)

    st.markdown(f"""
    <div class="machine-card {card_class}">
        <div class="machine-title">
            <span class="status-dot {dot_class}"></span>
            {row['machine_name']} — {row['line']}
        </div>
        <div class="machine-small">{row['machine_type']} • {row['product']}</div><br>

        <b>Status:</b> {row['status']} |
        <b>Risk:</b> {row['risk_level']} ({row['risk_score']}/100) |
        <b>Alarm:</b> {row['alarm']}<br>

        <b>Speed:</b> {row['speed']} / {row['target_speed']} |
        <b>Temperature:</b> {row['temperature']}°C |
        <b>Reject Rate:</b> {row['reject_rate']}%<br>

        <b>OEE:</b> {row['oee']:.1f}% |
        <b>Availability:</b> {row['availability']:.1f}% |
        <b>Performance:</b> {row['performance']:.1f}% |
        <b>Quality:</b> {row['quality']:.1f}%<br><br>

        <b>Reason:</b> {row['risk_reasons']}<br>
        <b>AI Recommendation:</b> {recommendation}
    </div>
    """, unsafe_allow_html=True)

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
    "availability",
    "performance",
    "quality",
    "oee",
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
    fig_oee_bar = px.bar(
        machine_df,
        x="machine_name",
        y="oee",
        color="risk_level",
        title="OEE by Machine"
    )
    st.plotly_chart(style_plotly(fig_oee_bar), use_container_width=True)

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
    st.markdown("""
    <div class="machine-card machine-good">
        ✅ All machines are operating within acceptable simulated limits.
    </div>
    """, unsafe_allow_html=True)
else:
    for _, row in high_risk_df.iterrows():
        st.markdown(f"""
        <div class="machine-card machine-risk">
            <b>{row['machine_name']}</b><br>
            ⚠️ <b>Risk detected:</b> {row['risk_reasons']}<br>
            ✅ <b>Recommended action:</b> {generate_ai_operator_recommendation(row)}
        </div>
        """, unsafe_allow_html=True)

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
