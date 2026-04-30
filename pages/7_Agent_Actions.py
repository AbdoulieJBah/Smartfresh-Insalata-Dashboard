import streamlit as st
from database import load_agent_actions, update_action_status

st.set_page_config(page_title="Agent Actions", layout="wide")

st.title("📋 Agent Actions — Task Tracking")

st.write(
    "Track AI-generated operational actions, assigned teams, priorities, and resolution status."
)

actions_df = load_agent_actions()

if actions_df.empty:
    st.info("No agent actions saved yet.")
    st.stop()

# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("Total Actions", len(actions_df))
c2.metric("Open", (actions_df["status"] == "Open").sum())
c3.metric("Resolved", (actions_df["status"] == "Resolved").sum())

st.markdown("---")

st.subheader("📌 Actions Table")
st.dataframe(actions_df, use_container_width=True)

st.markdown("---")

st.subheader("🔄 Update Action Status")

selected_id = st.selectbox(
    "Select Action ID",
    actions_df["id"].tolist()
)

selected_action = actions_df[actions_df["id"] == selected_id].iloc[0]

st.write(f"**Risk Type:** {selected_action['risk_type']}")
st.write(f"**Batch:** {selected_action['batch_id']}")
st.write(f"**Issue:** {selected_action['issue']}")
st.write(f"**Assigned Team:** {selected_action['assigned_team']}")
st.write(f"**Current Status:** {selected_action['status']}")

new_status = st.selectbox(
    "New Status",
    ["Open", "In Progress", "Resolved"],
    index=["Open", "In Progress", "Resolved"].index(selected_action["status"])
    if selected_action["status"] in ["Open", "In Progress", "Resolved"]
    else 0
)

if st.button("Update Status"):
    update_action_status(selected_id, new_status)
    st.success("✅ Action status updated.")
    st.rerun()
