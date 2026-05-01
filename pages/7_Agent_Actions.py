import streamlit as st
from database import (
    load_alerts,
    update_alert_status,
    load_agent_actions,
    update_action_status,
    load_agent_logs,
    load_stream_events
)

st.set_page_config(page_title="Agent Actions", layout="wide")

st.title("📋 Agent Actions & Alerts Center")

st.write(
    "Track AI-generated alerts, autonomous actions, priorities, assigned teams, "
    "streaming events, and resolution status."
)

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
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Saved Alerts", len(alerts_df))
c2.metric("Open Alerts", (alerts_df["status"] == "Open").sum() if not alerts_df.empty else 0)
c3.metric("Saved Actions", len(actions_df))
c4.metric("Open Actions", (actions_df["status"] == "Open").sum() if not actions_df.empty else 0)
c5.metric("Resolved Actions", (actions_df["status"] == "Resolved").sum() if not actions_df.empty else 0)

st.markdown("---")

# -----------------------------
# PRIORITY SUMMARY
# -----------------------------
st.subheader("🔥 Priority Overview")

if actions_df.empty:
    st.info("No action priority data yet.")
else:
    high_priority = actions_df[actions_df["priority_score"] >= 70]
    medium_priority = actions_df[
        (actions_df["priority_score"] >= 40) & (actions_df["priority_score"] < 70)
    ]
    low_priority = actions_df[actions_df["priority_score"] < 40]

    p1, p2, p3 = st.columns(3)
    p1.metric("High Priority", len(high_priority))
    p2.metric("Medium Priority", len(medium_priority))
    p3.metric("Low Priority", len(low_priority))

    st.dataframe(
        actions_df.sort_values(["priority_score", "created_at"], ascending=[False, False]),
        use_container_width=True
    )

st.markdown("---")

# -----------------------------
# FILTERS
# -----------------------------
st.subheader("🔎 Filter Actions")

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
    st.info("No actions available to filter.")

st.markdown("---")

# -----------------------------
# ALERTS CENTER
# -----------------------------
st.subheader("🚨 Saved Agent Alerts")

if alerts_df.empty:
    st.info("No alerts saved yet. Run the AI Production Agent first.")
else:
    st.dataframe(
        alerts_df.sort_values(["priority_score", "timestamp"], ascending=[False, False]),
        use_container_width=True
    )

    st.markdown("### 🔄 Update Alert Status")

    selected_alert_id = st.selectbox(
        "Select Alert ID",
        alerts_df["id"].tolist(),
        key="alert_id_select"
    )

    selected_alert = alerts_df[alerts_df["id"] == selected_alert_id].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Type", selected_alert["risk_type"])
    c2.metric("Severity", selected_alert["severity"])
    c3.metric("Priority", int(selected_alert["priority_score"]) if selected_alert["priority_score"] else 0)

    st.write(f"**Batch:** {selected_alert['batch_id']}")
    st.write(f"**Issue:** {selected_alert['issue']}")
    st.write(f"**Recommended Action:** {selected_alert['recommended_action']}")
    st.write(f"**Assigned Team:** {selected_alert.get('assigned_team', 'N/A')}")
    st.write(f"**Current Status:** {selected_alert['status']}")

    alert_status_options = ["Open", "In Progress", "Resolved"]

    new_alert_status = st.selectbox(
        "New Alert Status",
        alert_status_options,
        index=alert_status_options.index(selected_alert["status"])
        if selected_alert["status"] in alert_status_options else 0,
        key="alert_status_select"
    )

    if st.button("Update Alert Status"):
        update_alert_status(selected_alert_id, new_alert_status)
        st.success("✅ Alert status updated.")
        st.rerun()

st.markdown("---")

# -----------------------------
# ACTIONS CENTER
# -----------------------------
st.subheader("📌 Assigned Agent Actions")

if actions_df.empty:
    st.info("No actions created yet. Enable Autonomous Mode in AI Production Agent or create actions manually.")
else:
    st.dataframe(
        actions_df.sort_values(["priority_score", "created_at"], ascending=[False, False]),
        use_container_width=True
    )

    st.markdown("### 🔄 Update Action Status")

    selected_action_id = st.selectbox(
        "Select Action ID",
        actions_df["id"].tolist(),
        key="action_id_select"
    )

    selected_action = actions_df[actions_df["id"] == selected_action_id].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Type", selected_action["risk_type"])
    c2.metric("Assigned Team", selected_action["assigned_team"])
    c3.metric("Priority", int(selected_action["priority_score"]) if selected_action["priority_score"] else 0)

    st.write(f"**Batch:** {selected_action['batch_id']}")
    st.write(f"**Issue:** {selected_action['issue']}")
    st.write(f"**Recommended Action:** {selected_action['recommended_action']}")
    st.write(f"**Current Status:** {selected_action['status']}")

    if "source_alert_id" in selected_action.index:
        st.write(f"**Source Alert ID:** {selected_action['source_alert_id']}")

    if "resolved_at" in selected_action.index and selected_action["resolved_at"]:
        st.write(f"**Resolved At:** {selected_action['resolved_at']}")

    action_status_options = ["Open", "In Progress", "Resolved"]

    new_action_status = st.selectbox(
        "New Action Status",
        action_status_options,
        index=action_status_options.index(selected_action["status"])
        if selected_action["status"] in action_status_options else 0,
        key="action_status_select"
    )

    if st.button("Update Action Status"):
        update_action_status(selected_action_id, new_action_status)
        st.success("✅ Action status updated.")
        st.rerun()

st.markdown("---")

# -----------------------------
# STREAMING EVENTS
# -----------------------------
st.subheader("📡 Streaming Events Feed")

if stream_df.empty:
    st.info("No streaming events yet. Simulate live events from the AI Production Agent page.")
else:
    st.dataframe(stream_df, use_container_width=True)

st.markdown("---")

# -----------------------------
# AGENT LOGS
# -----------------------------
st.subheader("🧾 Agent Logs")

if logs_df.empty:
    st.info("No agent logs yet.")
else:
    st.dataframe(logs_df.head(50), use_container_width=True)
