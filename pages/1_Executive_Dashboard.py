import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_data, calculate_kpis
from auth_utils import require_role, get_current_user
from utils import setup_page, premium_hero, metric_card, insight_card, section_title, style_plotly

require_role(["Admin", "Manager"])

setup_page("Executive Dashboard")


# -----------------------------
# PREMIUM UI HELPERS
# -----------------------------
def inject_page_css():
    st.markdown("""
    <style>
    .section-title {
        font-size: 1.25rem;
        font-weight: 850;
        color: #ffffff;
        margin: 1.5rem 0 0.8rem 0;
    }

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

    .metric-card {
        padding: 20px;
        border-radius: 18px;
        background: rgba(15,23,42,0.88);
        border: 1px solid rgba(34,197,94,0.24);
        box-shadow: 0 12px 32px rgba(0,0,0,0.28);
        min-height: 125px;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.86rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.85rem;
        font-weight: 900;
        margin-top: 10px;
    }

    .metric-note {
        color: #86efac;
        font-size: 0.82rem;
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

    .insight-good {
        border-left: 4px solid #22c55e;
    }

    .insight-risk {
        border-left: 4px solid #f59e0b;
    }

    .chart-card {
        padding: 14px;
        border-radius: 18px;
        background: rgba(15,23,42,0.72);
        border: 1px solid rgba(34,197,94,0.16);
        box-shadow: 0 10px 26px rgba(0,0,0,0.24);
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


def insight_card(message, risk=False):
    css_class = "insight-risk" if risk else "insight-good"
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
st.markdown('<div class="section-title">📌 Executive KPIs</div>', unsafe_allow_html=True)

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
st.markdown('<div class="section-title">🧠 Executive Status Summary</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)

with s1:
    if kpis["waste_rate"] > 8:
        insight_card("⚠️ Waste rate is above target. Operations and Quality should review high-waste products.", risk=True)
    else:
        insight_card("✅ Waste rate appears under control.")

with s2:
    if kpis["defect_rate"] > 2:
        insight_card("⚠️ Defect rate is elevated. Supplier quality or production line issues may exist.", risk=True)
    else:
        insight_card("✅ Defect rate appears acceptable.")

with s3:
    if kpis["delayed"] > 0:
        insight_card("⚠️ Delivery delays detected. Logistics performance should be monitored.", risk=True)
    else:
        insight_card("✅ No major delivery delay issue detected.")

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
st.markdown('<div class="section-title">🏭 Production, Waste & Supplier Performance</div>', unsafe_allow_html=True)

chart1, chart2 = st.columns(2)

with chart1:
    fig = px.bar(
        product_summary,
        x="product_name",
        y=["quantity_produced", "quantity_sold"],
        barmode="group",
        title="Production vs Sales by Product"
    )
    fig = style_plotly(fig)
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    fig_waste = px.bar(
        product_summary.sort_values("waste_quantity", ascending=False),
        x="product_name",
        y="waste_quantity",
        title="Waste Quantity by Product"
    )
    fig_waste = style_plotly(fig_waste)
    st.plotly_chart(fig_waste, use_container_width=True)

chart3, chart4 = st.columns(2)

with chart3:
    fig_supplier = px.bar(
        supplier_summary.sort_values("supplier_risk_score", ascending=False),
        x="supplier",
        y=["waste_quantity", "defect_count"],
        barmode="group",
        title="Supplier Waste and Defects"
    )
    fig_supplier = style_plotly(fig_supplier)
    st.plotly_chart(fig_supplier, use_container_width=True)

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
            fig_revenue = style_plotly(fig_revenue)
            st.plotly_chart(fig_revenue, use_container_width=True)
        else:
            insight_card("No valid date values available for revenue trend.", risk=True)
    else:
        insight_card("Revenue trend requires date and revenue columns.", risk=True)

# -----------------------------
# KEY INSIGHTS
# -----------------------------
st.markdown('<div class="section-title">🔎 Key Executive Insights</div>', unsafe_allow_html=True)

i1, i2 = st.columns(2)

with i1:
    if not product_summary.empty:
        top_waste_product = product_summary.sort_values("waste_quantity", ascending=False).iloc[0]
        insight_card(
            f"♻️ Highest waste product: <b>{top_waste_product['product_name']}</b> "
            f"with <b>{top_waste_product['waste_quantity']:,.0f}</b> waste units.",
            risk=True
        )

with i2:
    if not supplier_summary.empty:
        top_supplier_risk = supplier_summary.sort_values("supplier_risk_score", ascending=False).iloc[0]
        insight_card(
            f"🏭 Supplier requiring attention: <b>{top_supplier_risk['supplier']}</b> "
            f"has the highest combined waste/defect risk.",
            risk=True
        )

# -----------------------------
# EXECUTIVE RECOMMENDATIONS
# -----------------------------
st.markdown('<div class="section-title">🎯 Executive Recommendations</div>', unsafe_allow_html=True)

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
    insight_card(f"✅ {rec}", risk=False)
