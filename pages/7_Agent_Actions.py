import streamlit as st
from auth_utils import require_role
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly

require_role(["Admin", "Manager", "Operations", "Logistics"])

from database import (
    load_alerts,
    update_alert_status,
    load_agent_actions,
    update_action_status,
    load_agent_logs,
    load_stream_events
)

setup_page("Agent Actions")


# -----------------------------
# PREMIUM UI HELPERS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .actions-hero {
        padding: 30px;
        border-radius: 26px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.97), rgba(6,78,59,0.78)),
            radial-gradient(circle at top right, rgba(34,197,94,0.24), transparent 35%);
        border: 1px solid rgba(34,197,94,0.36);
        box-shadow: 0 18px 50px rgba(0,0,0,0.38);
        margin-bottom: 24px;
    }

    .actions-hero h1 {
        font-size: 2.25rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .actions-hero p {
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
    </style>
    """, unsafe_allow_html=True)

inject_page_css()


# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class="actions-hero">
    <h1>📋 Agent Actions & Alerts Center</h1>
    <p>
        Track AI-generated alerts, autonomous actions, priorities, assigned teams,
        streaming events, and resolution status across SmartFresh operations.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------
alerts_df = load_alerts()
actions_df = load_agent_actions()
logs_df = load_agent_logs()
stream_df = load_stream_events(limit=30)

# -----------------------------
# ENSURE SAFE COLUMNS
# -----------------------------
if not alerts_df.empty:
    if "priority_score" not in alerts_df.columns:
        alerts_df["priority_score"] = 0
    if "assigned_team" not in alerts_df.columns:
        alerts_df["assigned_team"] = "Operations Team"

if not actions_df.empty:
    if "priority_score" not in actions_df.columns:
        actions_df["priority_score"] = 0
    if "assigned_team" not in actions_df.columns:
        actions_df["assigned_team"] = "Operations Team"

# -----------------------------
# KPI SUMMARY
# -----------------------------
st.markdown('<div class="section-title">📌 Execution KPIs</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    metric_card("Saved Alerts", f"{len(alerts_df)}", "AI alert records")

with c2:
    metric_card(
        "Open Alerts",
        f"{(alerts_df['status'] == 'Open').sum() if not alerts_df.empty else 0}",
        "Pending alert review"
    )

with c3:
    metric_card("Saved Actions", f"{len(actions_df)}", "Action records")

with c4:
    metric_card(
        "Open Actions",
        f"{(actions_df['status'] == 'Open').sum() if not actions_df.empty else 0}",
        "Pending execution"
    )

with c5:
    metric_card(
        "Resolved Actions",
        f"{(actions_df['status'] == 'Resolved').sum() if not actions_df.empty else 0}",
        "Completed tasks"
    )

# -----------------------------
# PRIORITY SUMMARY
# -----------------------------
st.markdown('<div class="section-title">🔥 Priority Overview</div>', unsafe_allow_html=True)

if actions_df.empty:
    insight_card("No action priority data yet.", level="risk")
else:
    high_priority = actions_df[actions_df["priority_score"] >= 70]
    medium_priority = actions_df[
        (actions_df["priority_score"] >= 40) & (actions_df["priority_score"] < 70)
    ]
    low_priority = actions_df[actions_df["priority_score"] < 40]

    p1, p2, p3 = st.columns(3)

    with p1:
        metric_card("High Priority", f"{len(high_priority)}", "Score ≥ 70")

    with p2:
        metric_card("Medium Priority", f"{len(medium_priority)}", "Score 40–69")

    with p3:
        metric_card("Low Priority", f"{len(low_priority)}", "Score < 40")

    st.dataframe(
        actions_df.sort_values(["priority_score", "created_at"], ascending=[False, False]),
        use_container_width=True
    )

# -----------------------------
# FILTERS
# -----------------------------
st.markdown('<div class="section-title">🔎 Filter Actions</div>', unsafe_allow_html=True)

if not actions_df.empty:
    f1, f2, f3 = st.columns(3)

    with f1:
        status_filter = st.selectbox(
            "Status",
            ["All", "Open", "In Progress", "Resolved"]
        )

    with f2:
        team_options = ["All"] + sorted(actions_df["assigned_team"].dropna().unique().tolist())
        team_filter = st.selectbox("Assigned Team", team_options)

    with f3:
        risk_options = ["All"] + sorted(actions_df["risk_type"].dropna().unique().tolist())
        risk_filter = st.selectbox("Risk Type", risk_options)

    filtered_actions = actions_df.copy()

    if status_filter != "All":
        filtered_actions = filtered_actions[filtered_actions["status"] == status_filter]

    if team_filter != "All":
        filtered_actions = filtered_actions[filtered_actions["assigned_team"] == team_filter]

    if risk_filter != "All":
        filtered_actions = filtered_actions[filtered_actions["risk_type"] == risk_filter]

    st.dataframe(
        filtered_actions.sort_values(["priority_score", "created_at"], ascending=[False, False]),
        use_container_width=True
    )
else:
    filtered_actions = actions_df
    insight_card("No actions available to filter.", level="risk")

# -----------------------------
# ALERTS CENTER
# -----------------------------
st.markdown('<div class="section-title">🚨 Saved Agent Alerts</div>', unsafe_allow_html=True)

if alerts_df.empty:
    insight_card("No alerts saved yet. Run the AI Production Agent first.", level="risk")
else:
    st.dataframe(
        alerts_df.sort_values(["priority_score", "timestamp"], ascending=[False, False]),
        use_container_width=True
    )

    st.markdown('<div class="section-title">🔄 Update Alert Status</div>', unsafe_allow_html=True)

    selected_alert_id = st.selectbox(
        "Select Alert ID",
        alerts_df["id"].tolist(),
        key="alert_id_select"
    )

    selected_alert = alerts_df[alerts_df["id"] == selected_alert_id].iloc[0]

    a1, a2, a3 = st.columns(3)

    with a1:
        metric_card("Risk Type", selected_alert["risk_type"], "Alert category")

    with a2:
        metric_card("Severity", selected_alert["severity"], "Risk level")

    with a3:
        metric_card(
            "Priority",
            f"{int(selected_alert['priority_score']) if selected_alert['priority_score'] else 0}",
            "Execution score"
        )

    insight_card(f"<b>Batch:</b> {selected_alert['batch_id']}", level="good")
    insight_card(f"<b>Issue:</b> {selected_alert['issue']}", level="risk")
    insight_card(f"<b>Recommended Action:</b> {selected_alert['recommended_action']}", level="good")
    insight_card(f"<b>Assigned Team:</b> {selected_alert.get('assigned_team', 'N/A')}", level="good")
    insight_card(f"<b>Current Status:</b> {selected_alert['status']}", level="good")

    alert_status_options = ["Open", "In Progress", "Resolved"]

    new_alert_status = st.selectbox(
        "New Alert Status",
        alert_status_options,
        index=alert_status_options.index(selected_alert["status"])
        if selected_alert["status"] in alert_status_options else 0,
        key="alert_status_select"
    )

    if st.button("Update Alert Status", use_container_width=True):
        update_alert_status(selected_alert_id, new_alert_status)
        st.success("✅ Alert status updated.")
        st.rerun()

# -----------------------------
# ACTIONS CENTER
# -----------------------------
st.markdown('<div class="section-title">📌 Assigned Agent Actions</div>', unsafe_allow_html=True)

if actions_df.empty:
    insight_card(
        "No actions created yet. Enable Autonomous Mode in AI Production Agent or create actions manually.",
        level="risk"
    )
else:
    st.dataframe(
        actions_df.sort_values(["priority_score", "created_at"], ascending=[False, False]),
        use_container_width=True
    )

    st.markdown('<div class="section-title">🔄 Update Action Status</div>', unsafe_allow_html=True)

    selected_action_id = st.selectbox(
        "Select Action ID",
        actions_df["id"].tolist(),
        key="action_id_select"
    )

    selected_action = actions_df[actions_df["id"] == selected_action_id].iloc[0]

    x1, x2, x3 = st.columns(3)

    with x1:
        metric_card("Risk Type", selected_action["risk_type"], "Action category")

    with x2:
        metric_card("Assigned Team", selected_action["assigned_team"], "Responsible team")

    with x3:
        metric_card(
            "Priority",
            f"{int(selected_action['priority_score']) if selected_action['priority_score'] else 0}",
            "Execution score"
        )

    insight_card(f"<b>Batch:</b> {selected_action['batch_id']}", level="good")
    insight_card(f"<b>Issue:</b> {selected_action['issue']}", level="risk")
    insight_card(f"<b>Recommended Action:</b> {selected_action['recommended_action']}", level="good")
    insight_card(f"<b>Current Status:</b> {selected_action['status']}", level="good")

    if "source_alert_id" in selected_action.index:
        insight_card(f"<b>Source Alert ID:</b> {selected_action['source_alert_id']}", level="good")

    if "resolved_at" in selected_action.index and selected_action["resolved_at"]:
        insight_card(f"<b>Resolved At:</b> {selected_action['resolved_at']}", level="good")

    action_status_options = ["Open", "In Progress", "Resolved"]

    new_action_status = st.selectbox(
        "New Action Status",
        action_status_options,
        index=action_status_options.index(selected_action["status"])
        if selected_action["status"] in action_status_options else 0,
        key="action_status_select"
    )

    if st.button("Update Action Status", use_container_width=True):
        update_action_status(selected_action_id, new_action_status)
        st.success("✅ Action status updated.")
        st.rerun()

# -----------------------------
# STREAMING EVENTS
# -----------------------------
st.markdown('<div class="section-title">📡 Streaming Events Feed</div>', unsafe_allow_html=True)

if stream_df.empty:
    insight_card("No streaming events yet. Simulate live events from the AI Production Agent page.", level="risk")
else:
    st.dataframe(stream_df, use_container_width=True)

# -----------------------------
# AGENT LOGS
# -----------------------------
st.markdown('<div class="section-title">🧾 Agent Logs</div>', unsafe_allow_html=True)

if logs_df.empty:
    insight_card("No agent logs yet.", level="risk")
else:
    st.dataframe(logs_df.head(50), use_container_width=True)
