import streamlit as st
import pandas as pd
import plotly.express as px

from utils import inject_css
from data_utils import load_data
from ai_utils import generate_ai_response_cached
from auth_utils import require_role
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly

require_role(["Admin", "Manager", "Operations", "Quality"])

setup_page("AI Copilot")

inject_css()

# -----------------------------
# PREMIUM UI HELPERS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .copilot-hero {
        padding: 30px;
        border-radius: 26px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.97), rgba(6,78,59,0.78)),
            radial-gradient(circle at top right, rgba(34,197,94,0.24), transparent 35%);
        border: 1px solid rgba(34,197,94,0.36);
        box-shadow: 0 18px 50px rgba(0,0,0,0.38);
        margin-bottom: 24px;
    }

    .copilot-hero h1 {
        font-size: 2.25rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .copilot-hero p {
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

    .agent-card {
        padding: 20px;
        border-radius: 18px;
        background: rgba(15,23,42,0.84);
        border: 1px solid rgba(34,197,94,0.22);
        box-shadow: 0 10px 28px rgba(0,0,0,0.26);
        color: #e5e7eb;
        min-height: 165px;
        margin-bottom: 10px;
    }

    .agent-title {
        color: #86efac;
        font-size: 1rem;
        font-weight: 850;
        margin-bottom: 10px;
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

    .question-chip {
        display: inline-block;
        padding: 10px 14px;
        border-radius: 999px;
        background: rgba(15,23,42,0.86);
        border: 1px solid rgba(34,197,94,0.25);
        color: #e5e7eb;
        font-weight: 650;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label, value, note=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def agent_card(title, body):
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{title}</div>
        <div>{body}</div>
    </div>
    """, unsafe_allow_html=True)


def insight_card(message, level="good"):
    css_class = {
        "good": "insight-good",
        "risk": "insight-risk",
        "critical": "insight-critical",
    }.get(level, "insight-good")

    st.markdown(f"""
    <div class="insight-card {css_class}">
        {message}
    </div>
    """, unsafe_allow_html=True)


def style_plotly(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        title_font=dict(size=18, color="#ffffff"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb")
        ),
        margin=dict(l=20, r=20, t=55, b=25),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.15)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.15)")
    return fig


inject_page_css()

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
st.markdown("""
<div class="copilot-hero">
    <h1>🤖 SmartFresh AI Copilot</h1>
    <p>
        Autonomous decision assistant for business intelligence, production risks, quality,
        logistics, and operational decision-making. Ask questions, trigger tools, and receive
        AI-generated recommendations grounded in operational data.
    </p>
</div>
""", unsafe_allow_html=True)

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
st.markdown('<div class="section-title">⚙️ Copilot Control Panel</div>', unsafe_allow_html=True)

control_1, control_2, control_3 = st.columns(3)

with control_1:
    auto_mode = st.toggle("🤖 Autonomous Copilot Mode", value=True)

with control_2:
    show_charts = st.toggle("📊 Show Charts", value=True)

with control_3:
    voice_ready = st.toggle("🎤 Voice-ready Mode", value=False)

insight_card(
    "Autonomous Mode generates proactive recommendations. Voice-ready Mode lets you paste dictated text.",
    level="good"
)

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

st.markdown('<div class="section-title">📌 Copilot Intelligence Snapshot</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    metric_card("Total Revenue", f"€{revenue_summary['total_revenue']:,.0f}", "Business value")
with c2:
    metric_card("Total Orders", f"{len(df)}", "Records monitored")
with c3:
    metric_card("Top Client", revenue_summary["top_client"], "Revenue leader")
with c4:
    metric_card("Delayed Deliveries", f"{risk_summary['delayed_deliveries']}", "Logistics risk")
with c5:
    metric_card("High Temp Records", f"{risk_summary['high_temperature_records']}", "Cold-chain risk")

# -----------------------------
# AUTONOMOUS MULTI-AGENT SUMMARY
# -----------------------------
if auto_mode:
    st.markdown('<div class="section-title">🧠 Autonomous Multi-Agent Intelligence</div>', unsafe_allow_html=True)

    bi_agent = f"""
    Total revenue is <b>€{revenue_summary['total_revenue']:,.2f}</b><br>
    Top client: <b>{revenue_summary['top_client']}</b><br>
    Revenue contribution: <b>€{revenue_summary['top_client_revenue']:,.2f}</b>
    """

    operations_agent = f"""
    Delayed deliveries: <b>{risk_summary['delayed_deliveries']}</b><br>
    High temperature records: <b>{risk_summary['high_temperature_records']}</b>
    """

    quality_agent = f"""
    Above-average waste records: <b>{risk_summary['above_average_waste_records']}</b><br>
    Above-average defect records: <b>{risk_summary['above_average_defect_records']}</b>
    """

    logistics_agent = """
    Delivery delays require dispatch review.<br>
    Prioritize delayed high-value client orders.
    """

    executive_agent = """
    Focus on revenue protection, supplier reliability, and operational bottlenecks.<br>
    Escalate high-risk suppliers and repeated delays.
    """

    a1, a2, a3 = st.columns(3)

    with a1:
        agent_card("📈 BI Agent", bi_agent)

    with a2:
        agent_card("🏭 Operations Agent", operations_agent)

    with a3:
        agent_card("🧪 Quality Agent", quality_agent)

    a4, a5 = st.columns(2)

    with a4:
        agent_card("🚚 Logistics Agent", logistics_agent)

    with a5:
        agent_card("👔 Executive Agent", executive_agent)

# -----------------------------
# CHARTS INSIDE COPILOT
# -----------------------------
if show_charts:
    st.markdown('<div class="section-title">📊 Copilot Visual Intelligence</div>', unsafe_allow_html=True)

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
        fig_client = style_plotly(fig_client)
        st.plotly_chart(fig_client, use_container_width=True)

    with chart2:
        supplier_perf = calculate_supplier_performance(df)

        fig_supplier = px.bar(
            supplier_perf,
            x="supplier",
            y="risk_score",
            title="Supplier Risk Score"
        )
        fig_supplier = style_plotly(fig_supplier)
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
        fig_trend = style_plotly(fig_trend)
        st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------------
# SUGGESTED QUESTIONS
# -----------------------------
st.markdown('<div class="section-title">💡 Suggested Questions</div>', unsafe_allow_html=True)

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
    if cols[i % 4].button(question, use_container_width=True):
        st.session_state.user_prompt = question
        st.rerun()

# -----------------------------
# VOICE-READY INPUT
# -----------------------------
if voice_ready:
    st.markdown('<div class="section-title">🎤 Voice-ready Input</div>', unsafe_allow_html=True)
    voice_text = st.text_area(
        "Paste dictated speech here",
        placeholder="Example: What should the operations team prioritize today?"
    )

    if st.button("Use Voice Text", use_container_width=True):
        st.session_state.user_prompt = voice_text
        st.rerun()

# -----------------------------
# CHAT INTERFACE
# -----------------------------
st.markdown('<div class="section-title">💬 Ask SmartFresh AI</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">🧠 Copilot Memory</div>', unsafe_allow_html=True)

if len(st.session_state.copilot_memory) == 0:
    insight_card("No memory yet. Ask a question to create memory.", level="risk")
else:
    memory_df = pd.DataFrame(st.session_state.copilot_memory)
    st.dataframe(memory_df.tail(10), use_container_width=True)

if st.button("🧹 Clear Copilot Memory", use_container_width=True):
    st.session_state.chat_history = []
    st.session_state.copilot_memory = []
    st.success("Memory cleared.")
    st.rerun()

# -----------------------------
# AUTONOMOUS DECISION OUTPUT
# -----------------------------
st.markdown('<div class="section-title">⚡ Autonomous Decision Recommendations</div>', unsafe_allow_html=True)

recommendations = []

if risk_summary["delayed_deliveries"] > 0:
    recommendations.append(("🚚 Logistics: Review delayed deliveries and prioritize high-value clients.", "risk"))

if risk_summary["high_temperature_records"] > 0:
    recommendations.append(("🌡️ Operations: Investigate cold-chain breaches immediately.", "critical"))

if risk_summary["above_average_waste_records"] > 0:
    recommendations.append(("📦 Quality: Review suppliers/products with above-average waste.", "risk"))

if revenue_trend and revenue_trend["drop_risk_percent"] > 5:
    recommendations.append(("📉 Management: Revenue trend shows possible decline risk. Review product mix and client demand.", "risk"))

if recommendations:
    for rec, level in recommendations:
        insight_card(rec, level=level)
else:
    insight_card("✅ No major autonomous decision alerts detected.")
