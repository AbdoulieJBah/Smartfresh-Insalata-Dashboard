import streamlit as st
import plotly.express as px
import pandas as pd

from data_utils import load_data, calculate_kpis
from auth_utils import require_role, get_current_user
from ai_utils import generate_ai_response_cached

from utils import (
    setup_page,
    metric_card,
    insight_card,
    section_title,
    style_plotly,
    set_copilot_context,
    render_global_copilot,
)

require_role(["Admin", "Manager", "Quality"])

setup_page("Business Intelligence", icon="📊")


# -----------------------------
# PAGE CSS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .bi-hero {
        padding: 28px;
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(6,78,59,0.76)),
            radial-gradient(circle at top right, rgba(34,197,94,0.22), transparent 35%);
        border: 1px solid rgba(34,197,94,0.35);
        box-shadow: 0 18px 48px rgba(0,0,0,0.35);
        margin-bottom: 24px;
    }

    .bi-hero h1 {
        font-size: 2.2rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .bi-hero p {
        color: #d1d5db;
        font-size: 1rem;
        line-height: 1.65;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)


inject_page_css()

# -----------------------------
# USER CONTEXT
# -----------------------------
user = get_current_user()
role = user.get("role", "User")

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

required_numeric_cols = [
    "revenue",
    "waste_quantity",
    "defect_count",
    "temperature",
    "rating",
    "quantity_sold",
    "quantity_produced",
]

for col in required_numeric_cols:
    if col not in df.columns:
        df[col] = 0

    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

if "client" not in df.columns:
    df["client"] = "Unknown"

if "supplier" not in df.columns:
    df["supplier"] = "Unknown"

if "product_name" not in df.columns:
    df["product_name"] = "Unknown Product"

if "delivery_status" not in df.columns:
    df["delivery_status"] = "Unknown"

if "batch_id" not in df.columns:
    df["batch_id"] = "N/A"

date_col = "date" if "date" in df.columns else "order_date"

kpis = calculate_kpis(df)

# -----------------------------
# COPILOT CONTEXT
# -----------------------------
set_copilot_context(f"""
Page: Business Intelligence

Role: {role}

Business Intelligence KPIs:
- Revenue: €{df['revenue'].sum():,.2f}
- Waste Rate: {kpis['waste_rate']:.2f}%
- Defect Rate: {kpis['defect_rate']:.2f}%
- Delayed Deliveries: {kpis['delayed']}
- Suppliers: {df['supplier'].nunique()}
- Clients: {df['client'].nunique()}

This page focuses on:
- Revenue analytics
- Supplier quality intelligence
- Operational risks
- Sentiment analysis
- Business trends
- Strategic recommendations
""")

# -----------------------------
# HEADER
# -----------------------------
st.markdown(f"""
<div class="bi-hero">
    <h1>📊 Business Intelligence</h1>
    <p>
        Welcome <b>{user.get('name', 'User')}</b>. You are viewing this page as <b>{role}</b>.
        This module combines revenue intelligence, supplier quality, operational analytics,
        customer sentiment, and strategic risk monitoring.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# KPIs
# -----------------------------
section_title("📌 Strategic KPIs")

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card(
        "Total Revenue",
        f"€{df['revenue'].sum():,.2f}",
        "Business performance"
    )

with c2:
    metric_card(
        "Clients",
        f"{df['client'].nunique()}",
        "Customer base"
    )

with c3:
    metric_card(
        "Suppliers",
        f"{df['supplier'].nunique()}",
        "Supplier network"
    )

with c4:
    metric_card(
        "Average Rating",
        f"{df['rating'].mean():.2f}",
        "Feedback quality"
    )

c5, c6, c7, c8 = st.columns(4)

with c5:
    metric_card(
        "Total Defects",
        f"{kpis['total_defects']:,}",
        "Quality exceptions"
    )

with c6:
    metric_card(
        "Defect Rate",
        f"{kpis['defect_rate']:.2f}%",
        "Target < 2%"
    )

with c7:
    metric_card(
        "Waste Rate",
        f"{kpis['waste_rate']:.2f}%",
        "Target < 8%"
    )

with c8:
    metric_card(
        "Delayed Deliveries",
        f"{kpis['delayed']}",
        "Logistics risk"
    )

# -----------------------------
# EXECUTIVE INSIGHTS
# -----------------------------
section_title("🧠 Strategic Intelligence")

if kpis["waste_rate"] > 8:
    insight_card(
        "⚠️ Waste rate exceeds operational target. Review supplier quality and production efficiency.",
        level="risk"
    )
else:
    insight_card(
        "✅ Waste performance currently stable.",
        level="good"
    )

if kpis["defect_rate"] > 2:
    insight_card(
        "⚠️ Defect rate is elevated. Production and supplier quality should be investigated.",
        level="risk"
    )
else:
    insight_card(
        "✅ Defect rate within acceptable threshold.",
        level="good"
    )

if kpis["delayed"] > 0:
    insight_card(
        "⚠️ Delayed deliveries detected. Logistics coordination should be reviewed.",
        level="risk"
    )
else:
    insight_card(
        "✅ Delivery operations stable.",
        level="good"
    )

# -----------------------------
# REVENUE ANALYTICS
# -----------------------------
section_title("💰 Revenue Analytics")

client_revenue = (
    df.groupby("client")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

product_revenue = (
    df.groupby("product_name")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

r1, r2 = st.columns(2)

with r1:
    fig_client = px.bar(
        client_revenue,
        x="client",
        y="revenue",
        title="Revenue by Client"
    )

    st.plotly_chart(
        style_plotly(fig_client),
        use_container_width=True
    )

with r2:
    fig_product = px.bar(
        product_revenue,
        x="product_name",
        y="revenue",
        title="Revenue by Product"
    )

    st.plotly_chart(
        style_plotly(fig_product),
        use_container_width=True
    )

# -----------------------------
# SUPPLIER ANALYTICS
# -----------------------------
section_title("🏭 Supplier Quality Intelligence")

supplier_perf = (
    df.groupby("supplier")
    .agg(
        total_waste=("waste_quantity", "sum"),
        total_defects=("defect_count", "sum"),
        avg_temperature=("temperature", "mean"),
        avg_rating=("rating", "mean"),
        total_revenue=("revenue", "sum")
    )
    .reset_index()
)

supplier_perf["quality_risk_score"] = (
    supplier_perf["total_waste"] * 0.4
    + supplier_perf["total_defects"] * 0.4
    + supplier_perf["avg_temperature"] * 10
)

supplier_perf = supplier_perf.sort_values(
    "quality_risk_score",
    ascending=False
)

s1, s2 = st.columns(2)

with s1:
    fig_supplier_risk = px.bar(
        supplier_perf,
        x="supplier",
        y="quality_risk_score",
        title="Supplier Risk Score"
    )

    st.plotly_chart(
        style_plotly(fig_supplier_risk),
        use_container_width=True
    )

with s2:
    fig_supplier_quality = px.bar(
        supplier_perf,
        x="supplier",
        y=["total_defects", "total_waste"],
        barmode="group",
        title="Supplier Waste and Defects"
    )

    st.plotly_chart(
        style_plotly(fig_supplier_quality),
        use_container_width=True
    )

st.dataframe(supplier_perf, use_container_width=True)

# -----------------------------
# TEMPERATURE RISK
# -----------------------------
section_title("🌡️ Temperature Risk Monitoring")

temp_issues = df[df["temperature"] > 6]

if len(temp_issues) > 0:

    insight_card(
        f"⚠️ {len(temp_issues)} temperature risk records detected.",
        level="risk"
    )

    cols = [
        "batch_id",
        "product_name",
        "supplier",
        "temperature",
        "defect_count",
        "waste_quantity"
    ]

    cols = [c for c in cols if c in temp_issues.columns]

    st.dataframe(
        temp_issues[cols],
        use_container_width=True
    )

else:
    insight_card(
        "✅ No temperature risk records detected.",
        level="good"
    )

# -----------------------------
# BUSINESS TRENDS
# -----------------------------
section_title("📈 Business Trends")

if date_col in df.columns:

    trend_df = df.copy()

    trend_df[date_col] = pd.to_datetime(
        trend_df[date_col],
        errors="coerce"
    )

    trend_df = (
        trend_df.dropna(subset=[date_col])
        .groupby(date_col)
        .agg(
            revenue=("revenue", "sum"),
            waste=("waste_quantity", "sum"),
            defects=("defect_count", "sum")
        )
        .reset_index()
        .sort_values(date_col)
    )

    t1, t2 = st.columns(2)

    with t1:
        fig_revenue = px.line(
            trend_df,
            x=date_col,
            y="revenue",
            title="Revenue Trend",
            markers=True
        )

        st.plotly_chart(
            style_plotly(fig_revenue),
            use_container_width=True
        )

    with t2:
        fig_waste = px.line(
            trend_df,
            x=date_col,
            y="waste",
            title="Waste Trend",
            markers=True
        )

        st.plotly_chart(
            style_plotly(fig_waste),
            use_container_width=True
        )

    fig_defects = px.line(
        trend_df,
        x=date_col,
        y="defects",
        title="Defect Trend",
        markers=True
    )

    st.plotly_chart(
        style_plotly(fig_defects),
        use_container_width=True
    )

else:
    insight_card(
        "Trend analysis requires date or order_date columns.",
        level="risk"
    )

# -----------------------------
# AI QUICK ACTIONS
# -----------------------------
section_title("🤖 AI Quick Actions")

qa1, qa2, qa3 = st.columns(3)

with qa1:
    if st.button(
        "📊 Explain BI Metrics",
        use_container_width=True
    ):
        st.session_state.global_copilot_history.append(
            (
                "user",
                "Explain the Business Intelligence metrics and identify the biggest risks."
            )
        )
        st.rerun()

with qa2:
    if st.button(
        "⚠️ Detect Strategic Risks",
        use_container_width=True
    ):
        st.session_state.global_copilot_history.append(
            (
                "user",
                "Identify strategic business and operational risks from this Business Intelligence page."
            )
        )
        st.rerun()

with qa3:
    if st.button(
        "🎯 Recommend Business Actions",
        use_container_width=True
    ):
        st.session_state.global_copilot_history.append(
            (
                "user",
                "Recommend the top business actions management should take based on this dashboard."
            )
        )
        st.rerun()

# -----------------------------
# DOWNLOAD
# -----------------------------
section_title("⬇️ Export Intelligence")

st.download_button(
    "Download Business Intelligence Report",
    df.to_csv(index=False),
    "smartfresh_business_intelligence_report.csv",
    "text/csv"
)

# -----------------------------
# GLOBAL AI COPILOT
# -----------------------------
render_global_copilot(generate_ai_response_cached)
