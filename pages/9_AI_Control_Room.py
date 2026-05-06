import time
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from auth_utils import require_role
from utils import setup_page, premium_hero, metric_card, section_title, style_plotly
from machine_simulator import (
    generate_operator_session,
    generate_industry_40_events,
    generate_ai_operator_recommendation,
    generate_control_room_summary,
)

require_role(["Admin", "Manager", "Operations", "Quality", "Logistics"])

setup_page("AI Control Room", icon="🧠")

# -----------------------------
# PAGE CSS
# -----------------------------
st.markdown("""
<style>
.control-room-card,
.machine-tile {
    background: rgba(15,23,42,0.84);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.35);
    margin-bottom: 18px;
    color: #e5e7eb;
    font-family: Inter, "Segoe UI", Arial, sans-serif !important;
    white-space: normal !important;
}

.control-room-card *,
.machine-tile * {
    font-family: Inter, "Segoe UI", Arial, sans-serif !important;
    white-space: normal !important;
}

.machine-running { border-left: 5px solid #22c55e; }
.machine-warning { border-left: 5px solid #f59e0b; }
.machine-critical { border-left: 5px solid #ef4444; }

.big-status {
    font-size: 1.35rem;
    font-weight: 950;
    color: #ffffff;
    margin-bottom: 10px;
}

.small-label {
    color: #9ca3af;
    font-size: 0.78rem;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
}

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

.info-row {
    margin-bottom: 7px;
    color: #e5e7eb;
    font-size: 0.94rem;
    line-height: 1.55;
}

.info-row strong {
    color: #ffffff;
    font-weight: 900;
}

.ai-command-box {
    background: linear-gradient(135deg, rgba(34,197,94,0.14), rgba(15,23,42,0.86));
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 20px;
    padding: 18px;
    color: #e5e7eb;
    margin-bottom: 18px;
}

.escalation-banner {
    padding: 18px 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(239,68,68,0.20), rgba(15,23,42,0.92));
    border: 1px solid rgba(239,68,68,0.50);
    box-shadow: 0 16px 40px rgba(239,68,68,0.16);
    margin-bottom: 18px;
    color: #f8fafc;
}

.warning-banner {
    padding: 18px 20px;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(245,158,11,0.16), rgba(15,23,42,0.90));
    border: 1px solid rgba(245,158,11,0.42);
    margin-bottom: 14px;
    color: #f8fafc;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
premium_hero(
    "🧠 AI Control Room",
    "Real-time Industry 4.0 command center for MES workflow, machine health, anomaly detection, OEE monitoring, and AI decision support.",
    badge="Industry 4.0 Command Center"
)

st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

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

# -----------------------------
# OEE LAYER
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

high_risk_df = machine_df[machine_df["risk_score"] >= alert_threshold]
critical_df = machine_df[machine_df["risk_level"] == "High"]

production_progress = session["produced_qty"] / session["ordered_qty"]

# -----------------------------
# AI ESCALATION BANNER
# -----------------------------
if not critical_df.empty:
    worst = critical_df.sort_values("risk_score", ascending=False).iloc[0]

    st.markdown(f"""
    <div class="escalation-banner">
        🚨 <strong>AI ESCALATION:</strong> Critical machine risk detected on <strong>{worst['machine']}</strong> — {worst['line']}
        <div class="info-row"><strong>Risk Score:</strong> {worst['risk_score']}/100</div>
        <div class="info-row"><strong>Main Cause:</strong> {worst['risk_reasons']}</div>
        <div class="info-row"><strong>AI Action:</strong> {worst['ai_recommendation']}</div>
    </div>
    """, unsafe_allow_html=True)

elif not high_risk_df.empty:
    worst = high_risk_df.sort_values("risk_score", ascending=False).iloc[0]

    st.markdown(f"""
    <div class="warning-banner">
        ⚠️ <strong>AI WARNING:</strong> Machine risk above threshold on <strong>{worst['machine']}</strong>
        <div class="info-row"><strong>Risk Score:</strong> {worst['risk_score']}/100</div>
        <div class="info-row"><strong>Recommended Action:</strong> {worst['ai_recommendation']}</div>
    </div>
    """, unsafe_allow_html=True)

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
# OEE STATUS
# -----------------------------
section_title("🏭 OEE Control Layer")

o1, o2, o3, o4 = st.columns(4)

with o1:
    metric_card("OEE", f"{avg_oee:.1f}%", "Overall effectiveness")

with o2:
    metric_card("Availability", f"{avg_availability:.1f}%", "Downtime impact")

with o3:
    metric_card("Performance", f"{avg_performance:.1f}%", "Speed vs target")

with o4:
    metric_card("Quality", f"{avg_quality:.1f}%", "Accepted output")

fig_oee = go.Figure(go.Indicator(
    mode="gauge+number",
    value=avg_oee,
    title={"text": "Control Room OEE %"},
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
# MES OPERATOR COMMAND PANEL
# -----------------------------
section_title("👷 MES Operator Command Panel")

left, right = st.columns([2, 1])

with left:
    st.markdown(f"""
    <div class="control-room-card">
        <div class="small-label">Current MES Work Order</div>
        <div class="big-status">{session['product']} — {session['phase']}</div>

        <div class="info-row"><strong>Client:</strong> {session['client']}</div>
        <div class="info-row"><strong>Destination:</strong> {session['destination']}</div>
        <div class="info-row"><strong>Operator:</strong> {session['operator']} | <strong>Shift:</strong> {session['shift']} | <strong>Start:</strong> {session['start_time']}</div>
        <div class="info-row"><strong>Status:</strong> {session['status']}</div>
        <div class="info-row"><strong>Notes:</strong> {session['notes']}</div>
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
    dot_class = "dot-green"

    if row["risk_level"] == "High":
        status_class = "machine-critical"
        dot_class = "dot-red"
    elif row["risk_level"] == "Medium":
        status_class = "machine-warning"
        dot_class = "dot-yellow"

    with cols[i % 2]:
        st.markdown(f"""
        <div class="machine-tile {status_class}">
            <div class="small-label">{row['line']} • {row['machine_type']}</div>

            <div class="big-status">
                <span class="status-dot {dot_class}"></span>
                {row['machine']}
            </div>

            <div class="info-row"><strong>Status:</strong> {row['status']} | <strong>Risk:</strong> {row['risk_level']} ({row['risk_score']}/100)</div>
            <div class="info-row"><strong>Speed:</strong> {row['speed']} / {row['target_speed']} | <strong>Temp:</strong> {row['temperature']}°C</div>
            <div class="info-row"><strong>Reject:</strong> {row['reject_rate']}% | <strong>Downtime:</strong> {row['downtime_minutes']} min | <strong>Vibration:</strong> {row['vibration']}</div>

            <div class="info-row" style="margin-top:12px;"><strong>OEE:</strong> {row['oee']:.1f}% | <strong>Availability:</strong> {row['availability']:.1f}%</div>
            <div class="info-row"><strong>Performance:</strong> {row['performance']:.1f}% | <strong>Quality:</strong> {row['quality']:.1f}%</div>

            <div class="info-row" style="margin-top:12px;"><strong>Reason:</strong> {row['risk_reasons']}</div>
            <div class="info-row"><strong>AI Action:</strong> {row['ai_recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# CONTROL ROOM ALERTS
# -----------------------------
section_title("🚨 Real-Time AI Alerts")

if high_risk_df.empty:
    st.markdown("""
    <div class="control-room-card">
        <div class="info-row">✅ No machines above the selected alert threshold.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for _, row in high_risk_df.sort_values("risk_score", ascending=False).iterrows():
        css_class = "machine-critical" if row["risk_level"] == "High" else "machine-warning"

        st.markdown(f"""
        <div class="machine-tile {css_class}">
            <div class="big-status">{row['machine']} requires attention</div>
            <div class="info-row"><strong>Risk Score:</strong> {row['risk_score']}/100</div>
            <div class="info-row"><strong>Cause:</strong> {row['risk_reasons']}</div>
            <div class="info-row"><strong>Recommended Action:</strong> {row['ai_recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)

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
        y=["speed", "target_speed"],
        barmode="group",
        title="Speed vs Target Speed"
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

with a4:
    fig = px.bar(
        machine_df,
        x="machine",
        y="oee",
        color="risk_level",
        title="OEE by Machine"
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

# -----------------------------
# AI COMMAND CENTER
# -----------------------------
section_title("🤖 AI Command Center")

st.markdown("""
<div class="ai-command-box">
    <div class="info-row"><strong>Ask the control room AI:</strong></div>
    <div class="info-row">Examples: Which machine should we check first? What is the biggest risk right now? Should production continue? What should the operator do next?</div>
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

        <div class="info-row">
            The first machine to check is <strong>{worst['machine']}</strong> because it currently has the highest
            risk score: <strong>{worst['risk_score']}/100</strong>.
        </div>

        <div class="info-row"><strong>Main issue:</strong> {worst['risk_reasons']}</div>
        <div class="info-row"><strong>Recommended action:</strong> {worst['ai_recommendation']}</div>
        <div class="info-row"><strong>Production decision:</strong> {decision}</div>
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
