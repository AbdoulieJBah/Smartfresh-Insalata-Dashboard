import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data
from ai_utils import generate_ai_response_cached
from auth_utils import require_role

require_role(["Admin", "Manager", "Operations", "Quality"])

st.set_page_config(page_title="AI Copilot", layout="wide")

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

# -----------------------------
# SAFE COLUMN SETUP
# -----------------------------
required_numeric_cols = [
    "revenue",
    "waste_quantity",
    "defect_count",
    "temperature",
    "quantity_sold",
    "quantity_produced",
]

for col in required_numeric_cols:
    if col not in df.columns:
        df[col] = 0

for col in required_numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

if "delivery_status" not in df.columns:
    df["delivery_status"] = "Unknown"

if "client" not in df.columns:
    df["client"] = df["customer"] if "customer" in df.columns else "Unknown"

if "supplier" not in df.columns:
    df["supplier"] = "Unknown"

if "product_name" not in df.columns:
    df["product_name"] = "Unknown Product"

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# -----------------------------
# HEADER
# -----------------------------
st.title("🤖 SmartFresh AI Copilot — Autonomous Decision Assistant")

st.write(
    "A multi-agent AI assistant for business intelligence, production risks, quality, logistics, "
    "and operational decision-making."
)

# -----------------------------
# SESSION MEMORY
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "copilot_memory" not in st.session_state:
    st.session_state.copilot_memory = []

if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = None

# -----------------------------
# CONTROL PANEL
# -----------------------------
auto_mode = st.toggle("🤖 Autonomous Copilot Mode", value=True)
show_charts = st.toggle("📊 Show Charts", value=True)
voice_ready = st.toggle("🎤 Voice-ready Mode", value=False)

st.caption(
    "Autonomous Mode generates proactive recommendations. Voice-ready Mode lets you paste dictated text."
)

st.markdown("---")

# -----------------------------
# TOOL EXECUTION FUNCTIONS
# -----------------------------
def calculate_revenue_summary(data):
    total_revenue = data["revenue"].sum()
    avg_revenue = data["revenue"].mean()

    if "client" in data.columns and not data.empty:
        top_client = (
            data.groupby("client")["revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(1)
        )
    else:
        top_client = None

    return {
        "total_revenue": round(total_revenue, 2),
        "avg_revenue": round(avg_revenue, 2),
        "top_client": top_client.index[0] if top_client is not None and len(top_client) else "N/A",
        "top_client_revenue": round(top_client.iloc[0], 2) if top_client is not None and len(top_client) else 0,
    }


def calculate_operations_risks(data):
    delayed = (data["delivery_status"].astype(str).str.lower() == "delayed").sum()
    high_temp = (data["temperature"] > 6).sum()
    high_waste = (data["waste_quantity"] > data["waste_quantity"].mean()).sum()
    high_defects = (data["defect_count"] > data["defect_count"].mean()).sum()

    return {
        "delayed_deliveries": int(delayed),
        "high_temperature_records": int(high_temp),
        "above_average_waste_records": int(high_waste),
        "above_average_defect_records": int(high_defects),
    }


def calculate_product_performance(data):
    product_perf = (
        data.groupby("product_name")
        .agg(
            revenue=("revenue", "sum"),
            waste=("waste_quantity", "sum"),
            defects=("defect_count", "sum"),
            quantity_sold=("quantity_sold", "sum")
        )
        .reset_index()
        .sort_values("revenue", ascending=False)
    )

    return product_perf


def calculate_supplier_performance(data):
    supplier_perf = (
        data.groupby("supplier")
        .agg(
            revenue=("revenue", "sum"),
            waste=("waste_quantity", "sum"),
            defects=("defect_count", "sum"),
            avg_temperature=("temperature", "mean")
        )
        .reset_index()
    )

    supplier_perf["risk_score"] = (
        supplier_perf["waste"] * 0.4
        + supplier_perf["defects"] * 0.4
        + supplier_perf["avg_temperature"] * 10
    )

    return supplier_perf.sort_values("risk_score", ascending=False)


def detect_revenue_trend(data):
    if "date" not in data.columns:
        return None

    trend = (
        data.dropna(subset=["date"])
        .groupby("date")["revenue"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    if len(trend) < 7:
        return None

    trend["rolling_3"] = trend["revenue"].rolling(3).mean()
    trend["rolling_7"] = trend["revenue"].rolling(7).mean()

    latest = trend.iloc[-1]

    if pd.isna(latest["rolling_3"]) or pd.isna(latest["rolling_7"]):
        return None

    drop_risk = (
        ((latest["rolling_7"] - latest["rolling_3"]) / latest["rolling_7"]) * 100
        if latest["rolling_7"] else 0
    )

    return {
        "latest_date": str(latest["date"].date()),
        "rolling_3_day_revenue": round(latest["rolling_3"], 2),
        "rolling_7_day_revenue": round(latest["rolling_7"], 2),
        "drop_risk_percent": round(drop_risk, 2),
    }


def run_tool(question, data):
    q = question.lower()

    if "revenue" in q or "client" in q:
        return "Revenue Tool", calculate_revenue_summary(data)

    if "risk" in q or "delay" in q or "temperature" in q or "waste" in q:
        return "Operations Risk Tool", calculate_operations_risks(data)

    if "product" in q:
        return "Product Performance Tool", calculate_product_performance(data).head(10).to_dict(orient="records")

    if "supplier" in q:
        return "Supplier Performance Tool", calculate_supplier_performance(data).head(10).to_dict(orient="records")

    return "General Operations Tool", {
        "records": len(data),
        "columns": list(data.columns)
    }

# -----------------------------
# KPI SUMMARY
# -----------------------------
revenue_summary = calculate_revenue_summary(df)
risk_summary = calculate_operations_risks(df)
revenue_trend = detect_revenue_trend(df)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Revenue", f"€{revenue_summary['total_revenue']:,.0f}")
c2.metric("Total Orders", len(df))
c3.metric("Top Client", revenue_summary["top_client"])
c4.metric("Delayed Deliveries", risk_summary["delayed_deliveries"])
c5.metric("High Temp Records", risk_summary["high_temperature_records"])

st.markdown("---")

# -----------------------------
# AUTONOMOUS MULTI-AGENT SUMMARY
# -----------------------------
if auto_mode:
    st.subheader("🧠 Autonomous Multi-Agent Intelligence")

    bi_agent = f"""
BI Agent:
- Total revenue is €{revenue_summary['total_revenue']:,.2f}
- Top client is {revenue_summary['top_client']} with €{revenue_summary['top_client_revenue']:,.2f}
"""

    operations_agent = f"""
Operations Agent:
- Delayed deliveries: {risk_summary['delayed_deliveries']}
- High temperature records: {risk_summary['high_temperature_records']}
"""

    quality_agent = f"""
Quality Agent:
- Above-average waste records: {risk_summary['above_average_waste_records']}
- Above-average defect records: {risk_summary['above_average_defect_records']}
"""

    logistics_agent = f"""
Logistics Agent:
- Delivery delays require dispatch review
- Prioritize delayed high-value client orders
"""

    executive_agent = f"""
Executive Agent:
- Focus on revenue protection, supplier reliability, and operational bottlenecks
- Escalate high-risk suppliers and repeated delays
"""

    tabs = st.tabs([
        "📈 BI Agent",
        "🏭 Operations Agent",
        "🧪 Quality Agent",
        "🚚 Logistics Agent",
        "👔 Executive Agent"
    ])

    with tabs[0]:
        st.info(bi_agent)

    with tabs[1]:
        st.warning(operations_agent)

    with tabs[2]:
        st.warning(quality_agent)

    with tabs[3]:
        st.info(logistics_agent)

    with tabs[4]:
        st.success(executive_agent)

st.markdown("---")

# -----------------------------
# CHARTS INSIDE COPILOT
# -----------------------------
if show_charts:
    st.subheader("📊 Copilot Visual Intelligence")

    chart1, chart2 = st.columns(2)

    with chart1:
        client_rev = (
            df.groupby("client")["revenue"]
            .sum()
            .reset_index()
            .sort_values("revenue", ascending=False)
        )

        fig_client = px.bar(
            client_rev,
            x="client",
            y="revenue",
            title="Revenue by Client"
        )
        st.plotly_chart(fig_client, use_container_width=True)

    with chart2:
        supplier_perf = calculate_supplier_performance(df)

        fig_supplier = px.bar(
            supplier_perf,
            x="supplier",
            y="risk_score",
            title="Supplier Risk Score"
        )
        st.plotly_chart(fig_supplier, use_container_width=True)

    if "date" in df.columns:
        revenue_daily = (
            df.dropna(subset=["date"])
            .groupby("date")["revenue"]
            .sum()
            .reset_index()
            .sort_values("date")
        )

        fig_trend = px.line(
            revenue_daily,
            x="date",
            y="revenue",
            title="Revenue Trend Over Time",
            markers=True
        )
        st.plotly_chart(fig_trend, use_container_width=True)

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
    "Which suppliers are risky?",
    "What should I prioritize today?",
    "Give me an executive summary",
    "What would the operations agent recommend?"
]

cols = st.columns(4)

for i, question in enumerate(suggestions):
    if cols[i % 4].button(question):
        st.session_state.user_prompt = question
        st.rerun()

# -----------------------------
# VOICE-READY INPUT
# -----------------------------
if voice_ready:
    st.subheader("🎤 Voice-ready Input")
    voice_text = st.text_area(
        "Paste dictated speech here",
        placeholder="Example: What should the operations team prioritize today?"
    )

    if st.button("Use Voice Text"):
        st.session_state.user_prompt = voice_text
        st.rerun()

st.markdown("---")

# -----------------------------
# CHAT INTERFACE
# -----------------------------
st.subheader("💬 Ask SmartFresh AI")

user_input = st.chat_input("Ask about operations, revenue, risks, suppliers, logistics...")

if st.session_state.user_prompt:
    user_input = st.session_state.user_prompt
    st.session_state.user_prompt = None

if user_input:
    st.session_state.chat_history.append(("user", user_input))

    tool_name, tool_result = run_tool(user_input, df)

    st.session_state.copilot_memory.append({
        "question": user_input,
        "tool_used": tool_name,
        "tool_result": tool_result
    })

    recent_memory = st.session_state.copilot_memory[-5:]

    context = f"""
You are SmartFresh AI Copilot, an autonomous decision assistant for a fresh produce operations platform.

You have access to:
- Business Intelligence Agent
- Operations Agent
- Quality Agent
- Logistics Agent
- Executive Agent

Dataset summary:
- Total records: {len(df)}
- Columns: {list(df.columns)}

Latest calculated tool used:
{tool_name}

Tool result:
{tool_result}

Recent memory:
{recent_memory}

User question:
{user_input}

Answer as an autonomous decision-making assistant.
Give clear business recommendations.
Use bullet points.
Highlight critical risks with ⚠️.
Include next actions.
"""

    with st.spinner("AI Copilot reasoning..."):
        response = generate_ai_response_cached(context)

    st.session_state.chat_history.append(("ai", response))

# -----------------------------
# DISPLAY CHAT MEMORY
# -----------------------------
for role, message in st.session_state.chat_history:
    if role == "user":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.markdown(message)

# -----------------------------
# MEMORY PANEL
# -----------------------------
st.markdown("---")
st.subheader("🧠 Copilot Memory")

if len(st.session_state.copilot_memory) == 0:
    st.info("No memory yet. Ask a question to create memory.")
else:
    memory_df = pd.DataFrame(st.session_state.copilot_memory)
    st.dataframe(memory_df.tail(10), use_container_width=True)

if st.button("🧹 Clear Copilot Memory"):
    st.session_state.chat_history = []
    st.session_state.copilot_memory = []
    st.success("Memory cleared.")
    st.rerun()

# -----------------------------
# AUTONOMOUS DECISION OUTPUT
# -----------------------------
st.markdown("---")
st.subheader("⚡ Autonomous Decision Recommendations")

recommendations = []

if risk_summary["delayed_deliveries"] > 0:
    recommendations.append("🚚 Logistics: Review delayed deliveries and prioritize high-value clients.")

if risk_summary["high_temperature_records"] > 0:
    recommendations.append("🌡️ Operations: Investigate cold-chain breaches immediately.")

if risk_summary["above_average_waste_records"] > 0:
    recommendations.append("📦 Quality: Review suppliers/products with above-average waste.")

if revenue_trend and revenue_trend["drop_risk_percent"] > 5:
    recommendations.append("📉 Management: Revenue trend shows possible decline risk. Review product mix and client demand.")

if recommendations:
    for rec in recommendations:
        st.warning(rec)
else:
    st.success("✅ No major autonomous decision alerts detected.")
