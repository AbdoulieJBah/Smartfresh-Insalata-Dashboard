import streamlit as st
from database import (
    load_alerts,
    update_alert_status,
    load_agent_actions,
    update_action_status
)

st.set_page_config(page_title="Agent Actions", layout="wide")

st.title("📋 Agent Actions & Alerts Center")

st.write(
    "Track AI-generated alerts, assigned actions, priorities, and resolution status."
)

# -----------------------------
# LOAD DATA
# -----------------------------
alerts_df = load_alerts()
actions_df = load_agent_actions()

# -----------------------------
# KPI SUMMARY
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Saved Alerts", len(alerts_df))
c2.metric("Open Alerts", (alerts_df["status"] == "Open").sum() if not alerts_df.empty else 0)
c3.metric("Saved Actions", len(actions_df))
c4.metric("Resolved Actions", (actions_df["status"] == "Resolved").sum() if not actions_df.empty else 0)

st.markdown("---")

# -----------------------------
# ALERTS CENTER
# -----------------------------
st.subheader("🚨 Saved Agent Alerts")

if alerts_df.empty:
    st.info("No alerts saved yet. Run the AI Production Agent first.")
else:
    st.dataframe(alerts_df, use_container_width=True)

    st.markdown("### 🔄 Update Alert Status")

    selected_alert_id = st.selectbox(
        "Select Alert ID",
        alerts_df["id"].tolist(),
        key="alert_id_select"
    )

    selected_alert = alerts_df[alerts_df["id"] == selected_alert_id].iloc[0]

    st.write(f"**Risk Type:** {selected_alert['risk_type']}")
    st.write(f"**Batch:** {selected_alert['batch_id']}")
    st.write(f"**Severity:** {selected_alert['severity']}")
    st.write(f"**Issue:** {selected_alert['issue']}")
    st.write(f"**Recommended Action:** {selected_alert['recommended_action']}")
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
    st.info("No actions created yet. Create actions from the AI Production Agent page.")
else:
    st.dataframe(actions_df, use_container_width=True)

    st.markdown("### 🔄 Update Action Status")

    selected_action_id = st.selectbox(
        "Select Action ID",
        actions_df["id"].tolist(),
        key="action_id_select"
    )

    selected_action = actions_df[actions_df["id"] == selected_action_id].iloc[0]

    st.write(f"**Risk Type:** {selected_action['risk_type']}")
    st.write(f"**Batch:** {selected_action['batch_id']}")
    st.write(f"**Issue:** {selected_action['issue']}")
    st.write(f"**Assigned Team:** {selected_action['assigned_team']}")
    st.write(f"**Current Status:** {selected_action['status']}")

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
