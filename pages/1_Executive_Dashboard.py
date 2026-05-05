import streamlit as st
import pandas as pd
import plotly.express as px

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

require_role(["Admin", "Manager"])

setup_page("Executive Dashboard", icon="📊")


# -----------------------------
# PAGE CSS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .hero-dashboard {
        padding: 28px;
        border-radius: 24px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.96), rgba(6,78,59,0.75)),
            radial-gradient(circle at top right, rgba(34,197,94,0.22), transparent 35%);
        border: 1px solid rgba(34,197,94,0.35);
        box-shadow: 0 18px 48px rgba(0,0,0,0.35);
        margin-bottom: 24px;
    }

    .hero-dashboard h1 {
        font-size: 2.25rem;
        font-weight: 950;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .hero-dashboard p {
        color: #d1d5db;
        font-size: 1rem;
        line-height: 1.65;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)


def ensure_columns(data):
    defaults = {
        "product_name": "Unknown Product",
        "supplier": "Unknown Supplier",
        "date": None,
        "revenue": 0,
        "quantity_produced": 0,
        "quantity_sold": 0,
        "waste_quantity": 0,
        "defect_count": 0,
    }

    for col, default in defaults.items():
        if col not in data.columns:
            data[col] = default

    numeric_cols = [
        "revenue",
        "quantity_produced",
        "quantity_sold",
        "waste_quantity",
        "defect_count",
    ]

    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    return data


inject_page_css()

# -----------------------------
# LOAD DATA
# -----------------------------
user = get_current_user()

df = load_data()
df.columns = df.columns.str.strip().str.lower()
df = ensure_columns(df)

kpis = calculate_kpis(df)

# -----------------------------
# COPILOT CONTEXT
# -----------------------------
set_copilot_context(f"""
Page: Executive Dashboard

This page gives leadership a strategic overview of production, sales, waste, defects, revenue, inventory, supplier performance, and logistics.

Executive KPIs:
- Total Production: {kpis['total_production']}
- Total Sales: {kpis['total_sales']}
- Waste Rate: {kpis['waste_rate']:.2f}%
- Revenue: €{kpis['revenue']:,.2f}
- Stock Remaining: {kpis['stock_remaining']}
- Total Waste: {kpis['total_waste']}
- Defect Rate: {kpis['defect_rate']:.2f}%
- Delayed Deliveries: {kpis['delayed']}

Leadership interpretation:
- Waste above 8% should be treated as operational/quality risk.
- Defect rate above 2% should trigger supplier or production review.
- Any delayed deliveries require logistics monitoring.
""")

# -----------------------------
# HEADER
# -----------------------------
st.markdown(f"""
<div class="hero-dashboard">
    <h1>📊 Executive Dashboard</h1>
    <p>
        Welcome <b>{user.get('name', 'User')}</b>. This strategic dashboard gives leadership a real-time view of
        production, sales, waste, defects, revenue, supplier quality, and logistics performance.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# EXECUTIVE KPIs
# -----------------------------
section_title("📌 Executive KPIs")

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card("Total Production", f"{kpis['total_production']:,}", "Production volume monitored")

with c2:
    metric_card("Total Sales", f"{kpis['total_sales']:,}", "Units sold")

with c3:
    metric_card("Waste Rate", f"{kpis['waste_rate']:.2f}%", "Target threshold: 8%")

with c4:
    metric_card("Revenue", f"€{kpis['revenue']:,.2f}", "Total commercial value")

c5, c6, c7, c8 = st.columns(4)

with c5:
    metric_card("Stock Remaining", f"{kpis['stock_remaining']:,}", "Available inventory")

with c6:
    metric_card("Total Waste", f"{kpis['total_waste']:,}", "Waste quantity")

with c7:
    metric_card("Defect Rate", f"{kpis['defect_rate']:.2f}%", "Target threshold: 2%")

with c8:
    metric_card("Delayed Deliveries", f"{kpis['delayed']}", "Logistics exceptions")

# -----------------------------
# EXECUTIVE STATUS SUMMARY
# -----------------------------
section_title("🧠 Executive Status Summary")

s1, s2, s3 = st.columns(3)

with s1:
    if kpis["waste_rate"] > 8:
        insight_card(
            "⚠️ Waste rate is above target. Operations and Quality should review high-waste products.",
            level="risk"
        )
    else:
        insight_card("✅ Waste rate appears under control.", level="good")

with s2:
    if kpis["defect_rate"] > 2:
        insight_card(
            "⚠️ Defect rate is elevated. Supplier quality or production line issues may exist.",
            level="risk"
        )
    else:
        insight_card("✅ Defect rate appears acceptable.", level="good")

with s3:
    if kpis["delayed"] > 0:
        insight_card(
            "⚠️ Delivery delays detected. Logistics performance should be monitored.",
            level="risk"
        )
    else:
        insight_card("✅ No major delivery delay issue detected.", level="good")

# -----------------------------
# DATA SUMMARIES
# -----------------------------
product_summary = (
    df.groupby("product_name")[["quantity_produced", "quantity_sold", "waste_quantity"]]
    .sum()
    .reset_index()
)

supplier_summary = (
    df.groupby("supplier")[["waste_quantity", "defect_count"]]
    .sum()
    .reset_index()
)

supplier_summary["supplier_risk_score"] = (
    supplier_summary["waste_quantity"] * 0.4
    + supplier_summary["defect_count"] * 0.6
)

# -----------------------------
# CHARTS
# -----------------------------
section_title("🏭 Production, Waste & Supplier Performance")

chart1, chart2 = st.columns(2)

with chart1:
    fig = px.bar(
        product_summary,
        x="product_name",
        y=["quantity_produced", "quantity_sold"],
        barmode="group",
        title="Production vs Sales by Product"
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

with chart2:
    fig_waste = px.bar(
        product_summary.sort_values("waste_quantity", ascending=False),
        x="product_name",
        y="waste_quantity",
        title="Waste Quantity by Product"
    )
    st.plotly_chart(style_plotly(fig_waste), use_container_width=True)

chart3, chart4 = st.columns(2)

with chart3:
    fig_supplier = px.bar(
        supplier_summary.sort_values("supplier_risk_score", ascending=False),
        x="supplier",
        y=["waste_quantity", "defect_count"],
        barmode="group",
        title="Supplier Waste and Defects"
    )
    st.plotly_chart(style_plotly(fig_supplier), use_container_width=True)

with chart4:
    if "date" in df.columns and "revenue" in df.columns:
        revenue_df = df.copy()
        revenue_df["date"] = pd.to_datetime(revenue_df["date"], errors="coerce")

        revenue_trend = (
            revenue_df.dropna(subset=["date"])
            .groupby("date")["revenue"]
            .sum()
            .reset_index()
            .sort_values("date")
        )

        if not revenue_trend.empty:
            fig_revenue = px.line(
                revenue_trend,
                x="date",
                y="revenue",
                title="Revenue Trend Over Time",
                markers=True
            )
            st.plotly_chart(style_plotly(fig_revenue), use_container_width=True)
        else:
            insight_card("No valid date values available for revenue trend.", level="risk")
    else:
        insight_card("Revenue trend requires date and revenue columns.", level="risk")

# -----------------------------
# KEY INSIGHTS
# -----------------------------
section_title("🔎 Key Executive Insights")

i1, i2 = st.columns(2)

with i1:
    if not product_summary.empty:
        top_waste_product = product_summary.sort_values("waste_quantity", ascending=False).iloc[0]
        insight_card(
            f"♻️ Highest waste product: <b>{top_waste_product['product_name']}</b> "
            f"with <b>{top_waste_product['waste_quantity']:,.0f}</b> waste units.",
            level="risk"
        )

with i2:
    if not supplier_summary.empty:
        top_supplier_risk = supplier_summary.sort_values("supplier_risk_score", ascending=False).iloc[0]
        insight_card(
            f"🏭 Supplier requiring attention: <b>{top_supplier_risk['supplier']}</b> "
            f"has the highest combined waste/defect risk.",
            level="risk"
        )

# -----------------------------
# EXECUTIVE AI QUICK ACTIONS
# -----------------------------
section_title("🤖 Executive AI Quick Actions")

ai1, ai2, ai3 = st.columns(3)

with ai1:
    if st.button("💡 Explain Executive KPIs", use_container_width=True):
        st.session_state.global_copilot_history.append(
            ("user", "Explain the executive KPIs and highlight the biggest risks.")
        )
        st.rerun()

with ai2:
    if st.button("⚠️ Identify Strategic Risks", use_container_width=True):
        st.session_state.global_copilot_history.append(
            ("user", "Identify the biggest strategic risks from this dashboard.")
        )
        st.rerun()

with ai3:
    if st.button("🎯 Recommend Management Actions", use_container_width=True):
        st.session_state.global_copilot_history.append(
            ("user", "Recommend the top management actions based on this dashboard.")
        )
        st.rerun()

# -----------------------------
# EXECUTIVE RECOMMENDATIONS
# -----------------------------
section_title("🎯 Executive Recommendations")

recommendations = []

if kpis["waste_rate"] > 8:
    recommendations.append("Prioritize waste reduction initiatives on high-waste products.")

if kpis["defect_rate"] > 2:
    recommendations.append("Review supplier quality performance and investigate defect-heavy suppliers.")

if kpis["delayed"] > 0:
    recommendations.append("Escalate delivery delays to logistics and review dispatch planning.")

if not recommendations:
    recommendations.append("Continue monitoring operations. Current performance appears stable.")

for rec in recommendations:
    insight_card(f"✅ {rec}", level="good")

# -----------------------------
# GLOBAL COPILOT
# -----------------------------
render_global_copilot(generate_ai_response_cached)
