import time
import streamlit as st
import plotly.express as px

from auth_utils import require_role
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly
from machine_simulator import (
    generate_operator_session,
    generate_industry_40_events,
    generate_ai_operator_recommendation,
    generate_control_room_summary,
)

require_role(["Admin", "Manager", "Operations", "Quality", "Logistics"])

setup_page("AI Control Room", icon="🧠")

premium_hero(
    "🧠 AI Control Room",
    "Real-time Industry 4.0 command center for MES workflow, machine health, anomaly detection, and AI decision support."
)

# -----------------------------
# CONTROL ROOM CSS
# -----------------------------
st.markdown("""
<style>
.control-room-card {
    background: rgba(15,23,42,0.82);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.35);
    margin-bottom: 14px;
}

.machine-tile {
    background: rgba(15,23,42,0.85);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid rgba(34,197,94,0.25);
    margin-bottom: 12px;
}

.machine-running {
    border-left: 5px solid #22c55e;
}

.machine-warning {
    border-left: 5px solid #f59e0b;
}

.machine-critical {
    border-left: 5px solid #ef4444;
}

.big-status {
    font-size: 1.45rem;
    font-weight: 950;
    color: #ffffff;
}

.small-label {
    color: #9ca3af;
    font-size: 0.82rem;
    font-weight: 800;
    text-transform: uppercase;
}

.ai-command-box {
    background: linear-gradient(135deg, rgba(34,197,94,0.14), rgba(15,23,42,0.86));
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 20px;
    padding: 18px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CONTROLS
# -----------------------------
section_title("⚙️ Control Room Settings")

c1, c2, c3, c4 = st.columns(4)

with c1:
    live_mode = st.toggle("📡 Live Control Room", value=False)

with c2:
    refresh_seconds = st.slider("Refresh seconds", 2, 20, 5)

with c3:
    show_raw = st.toggle("📋 Show Raw Feed", value=False)

with c4:
    alert_threshold = st.slider("Alert Threshold", 40, 90, 60)

# -----------------------------
# DATA
# -----------------------------
session = generate_operator_session()
machine_df = generate_industry_40_events()

machine_df["ai_recommendation"] = machine_df.apply(
    generate_ai_operator_recommendation,
    axis=1
)

summary = generate_control_room_summary(machine_df, session)

high_risk_df = machine_df[machine_df["risk_score"] >= alert_threshold]
critical_df = machine_df[machine_df["risk_level"] == "High"]

production_progress = session["produced_qty"] / session["ordered_qty"]

# -----------------------------
# TOP STATUS BAR
# -----------------------------
section_title("🏭 Factory Line Status")

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    metric_card("Line", summary["line"], "Active production line")

with k2:
    metric_card("Work Order", summary["work_order"], "MES order")

with k3:
    metric_card("Product", summary["product"], "Current product")

with k4:
    metric_card("Machines", summary["machines"], "Connected assets")

with k5:
    metric_card("Critical", len(critical_df), "High-risk machines")

with k6:
    metric_card("Avg Risk", summary["avg_risk_score"], "Control-room score")

# -----------------------------
# MES OPERATOR COMMAND PANEL
# -----------------------------
section_title("👷 MES Operator Command Panel")

left, right = st.columns([2, 1])

with left:
    st.markdown(f"""
    <div class="control-room-card">
        <div class="small-label">Current MES Work Order</div>
        <div class="big-status">{session['product']} — {session['phase']}</div>
        <br>
        <b>Client:</b> {session['client']}<br>
        <b>Destination:</b> {session['destination']}<br>
        <b>Operator:</b> {session['operator']} |
        <b>Shift:</b> {session['shift']} |
        <b>Start:</b> {session['start_time']}<br>
        <b>Status:</b> {session['status']}<br>
        <b>Notes:</b> {session['notes']}
    </div>
    """, unsafe_allow_html=True)

with right:
    metric_card("Produced", f"{session['produced_qty']:,}", "MES output")
    metric_card("Remaining", f"{session['remaining']:,}", "Open quantity")

st.progress(production_progress)

# -----------------------------
# MACHINE WALL
# -----------------------------
section_title("🖥️ Machine Wall — Live Industrial Assets")

cols = st.columns(2)

for i, row in machine_df.iterrows():
    status_class = "machine-running"

    if row["risk_level"] == "High":
        status_class = "machine-critical"
    elif row["risk_level"] == "Medium":
        status_class = "machine-warning"

    with cols[i % 2]:
        st.markdown(f"""
        <div class="machine-tile {status_class}">
            <div class="small-label">{row['line']} • {row['machine_type']}</div>
            <div class="big-status">{row['machine']}</div>
            <br>
            <b>Status:</b> {row['status']} |
            <b>Risk:</b> {row['risk_level']} ({row['risk_score']}/100)<br>
            <b>Speed:</b> {row['speed']} |
            <b>Target:</b> {row['target_speed']} |
            <b>Temp:</b> {row['temperature']}°C<br>
            <b>Reject:</b> {row['reject_rate']}% |
            <b>Downtime:</b> {row['downtime_minutes']} min |
            <b>Vibration:</b> {row['vibration']}<br><br>
            <b>Reason:</b> {row['risk_reasons']}<br>
            <b>AI Action:</b> {row['ai_recommendation']}
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# CONTROL ROOM ALERTS
# -----------------------------
section_title("🚨 Real-Time AI Alerts")

if high_risk_df.empty:
    insight_card("✅ No machines above the selected alert threshold.", level="good")
else:
    for _, row in high_risk_df.sort_values("risk_score", ascending=False).iterrows():
        level = "critical" if row["risk_level"] == "High" else "risk"

        insight_card(
            f"""
            <b>{row['machine']}</b> requires attention.<br>
            <b>Risk Score:</b> {row['risk_score']}/100<br>
            <b>Cause:</b> {row['risk_reasons']}<br>
            <b>Recommended Action:</b> {row['ai_recommendation']}
            """,
            level=level
        )

# -----------------------------
# ANALYTICS WALL
# -----------------------------
section_title("📊 Control Room Analytics Wall")

a1, a2 = st.columns(2)

with a1:
    fig = px.bar(
        machine_df.sort_values("risk_score", ascending=False),
        x="machine",
        y="risk_score",
        color="risk_level",
        title="Machine Risk Ranking"
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

with a2:
    fig = px.scatter(
        machine_df,
        x="temperature",
        y="reject_rate",
        size="risk_score",
        color="risk_level",
        hover_name="machine",
        title="Temperature vs Reject Rate"
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

a3, a4 = st.columns(2)

with a3:
    fig = px.bar(
        machine_df,
        x="machine",
        y=["speed", "downtime_minutes"],
        barmode="group",
        title="Speed vs Downtime"
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

with a4:
    fig = px.bar(
        machine_df,
        x="machine",
        y="vibration",
        color="risk_level",
        title="Vibration Signal by Machine"
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

# -----------------------------
# AI COMMAND CENTER
# -----------------------------
section_title("🤖 AI Command Center")

st.markdown("""
<div class="ai-command-box">
<b>Ask the control room AI:</b><br>
Examples:
<ul>
<li>Which machine should we check first?</li>
<li>What is the biggest risk right now?</li>
<li>Should production continue?</li>
<li>What should the operator do next?</li>
</ul>
</div>
""", unsafe_allow_html=True)

question = st.text_input(
    "Ask AI Control Room",
    placeholder="Example: Which machine should we check first?"
)

if question:
    worst = machine_df.sort_values("risk_score", ascending=False).iloc[0]

    decision = (
        "Escalate immediately before continuing normal production."
        if worst["risk_score"] >= 70
        else "Continue monitoring while the operator reviews the issue."
    )

    st.markdown(f"""
    <div class="control-room-card">
        <div class="small-label">AI Operator Answer</div>
        <div class="big-status">{worst['machine']}</div>
        <br>
        The first machine to check is <b>{worst['machine']}</b> because it currently has the highest
        risk score: <b>{worst['risk_score']}/100</b>.<br><br>
        <b>Main issue:</b> {worst['risk_reasons']}<br>
        <b>Recommended action:</b> {worst['ai_recommendation']}<br>
        <b>Production decision:</b> {decision}
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# RAW FEED
# -----------------------------
if show_raw:
    section_title("📋 Raw Machine Event Feed")
    st.dataframe(machine_df, use_container_width=True)

# -----------------------------
# DOWNLOAD
# -----------------------------
st.download_button(
    "Download Control Room Machine Feed",
    machine_df.to_csv(index=False),
    "smartfresh_ai_control_room_feed.csv",
    "text/csv",
    use_container_width=True
)

# -----------------------------
# LIVE REFRESH
# -----------------------------
if live_mode:
    time.sleep(refresh_seconds)
    st.rerun()
