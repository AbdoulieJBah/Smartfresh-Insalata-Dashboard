import streamlit as st
import pandas as pd
from data_utils import load_data
from ai_utils import generate_ai_response
from auth_utils import require_role

require_role(["Admin", "Manager", "Operations", "Quality", "Logistics"])

st.set_page_config(page_title="AI Copilot", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
### 🤖 SmartFresh AI Copilot
Ask questions about production, revenue, risks, logistics, and operations.
""")

st.markdown("---")

# -----------------------------
# QUICK INSIGHTS (BI STYLE)
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"€{df['revenue'].sum():,.0f}" if "revenue" in df.columns else "N/A")
c2.metric("Total Orders", len(df))
c3.metric("Avg Temperature", f"{df['temperature'].mean():.1f}°C" if "temperature" in df.columns else "N/A")
c4.metric("Delayed Deliveries",
          (df["delivery_status"].astype(str).str.lower() == "delayed").sum()
          if "delivery_status" in df.columns else 0)

st.markdown("---")

# -----------------------------
# SUGGESTED QUESTIONS
# -----------------------------
st.subheader("💡 Suggested Questions")

suggestions = [
    "Why did revenue drop recently?",
    "Which clients generate the most revenue?",
    "What are the biggest operational risks?",
    "Which products have highest waste?",
    "Show me delivery delays impact",
    "What should I prioritize today?"
]

cols = st.columns(3)

for i, question in enumerate(suggestions):
    if cols[i % 3].button(question):
        st.session_state["user_prompt"] = question

st.markdown("---")

# -----------------------------
# CHAT INTERFACE
# -----------------------------
st.subheader("💬 Ask SmartFresh AI")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.chat_input("Ask about operations, revenue, risks...")

if "user_prompt" in st.session_state:
    user_input = st.session_state.pop("user_prompt")

# Handle input
if user_input:
    st.session_state.chat_history.append(("user", user_input))

    # Build context-aware prompt
    context = f"""
You are an AI assistant for a fresh produce company.

Dataset summary:
- Total records: {len(df)}
- Columns: {list(df.columns)}

Answer this business question:
{user_input}

Give insights, not generic answers.
Use bullet points.
Highlight important risks with ⚠️.
"""

    with st.spinner("AI thinking..."):
        response = generate_ai_response(context)

    st.session_state.chat_history.append(("ai", response))

# -----------------------------
# DISPLAY CHAT
# -----------------------------
for role, message in st.session_state.chat_history:
    if role == "user":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.markdown(message)

# -----------------------------
# QUICK ACTIONS
# -----------------------------
st.markdown("---")
st.subheader("⚡ Quick AI Actions")

qa1, qa2, qa3 = st.columns(3)

if qa1.button("📉 Explain Revenue"):
    st.session_state["user_prompt"] = "Explain recent revenue performance and issues"

if qa2.button("⚠️ Show Risks"):
    st.session_state["user_prompt"] = "What are the biggest operational risks right now?"

if qa3.button("📦 Optimize Operations"):
    st.session_state["user_prompt"] = "What actions should operations team take today?"
