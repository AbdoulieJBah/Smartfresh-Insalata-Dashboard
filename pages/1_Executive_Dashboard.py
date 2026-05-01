import streamlit as st
import plotly.express as px
from data_utils import load_data, calculate_kpis
from auth_utils import require_role, get_current_user

require_role(["Admin", "Manager"])

st.set_page_config(page_title="Executive Dashboard", layout="wide")

# -----------------------------
# USER CONTEXT
# -----------------------------
user = get_current_user()

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Executive Dashboard — Strategic Operations Overview")

st.write(
    f"Welcome **{user.get('name', 'User')}**. "
    "This dashboard provides an executive-level view of production, sales, waste, defects, revenue, and supplier performance."
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()
df.columns = df.columns.str.strip().str.lower()

kpis = calculate_kpis(df)

# -----------------------------
# EXECUTIVE KPI CARDS
# -----------------------------
st.subheader("📌 Executive KPIs")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Production", f"{kpis['total_production']:,}")
c2.metric("Total Sales", f"{kpis['total_sales']:,}")
c3.metric("Waste Rate", f"{kpis['waste_rate']:.2f}%")
c4.metric("Revenue", f"€{kpis['revenue']:,.2f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Stock Remaining", f"{kpis['stock_remaining']:,}")
c6.metric("Total Waste", f"{kpis['total_waste']:,}")
c7.metric("Defect Rate", f"{kpis['defect_rate']:.2f}%")
c8.metric("Delayed Deliveries", kpis["delayed"])

st.markdown("---")

# -----------------------------
# EXECUTIVE STATUS SUMMARY
# -----------------------------
st.subheader("🧠 Executive Status Summary")

summary_messages = []

if kpis["waste_rate"] > 8:
    summary_messages.append("⚠️ Waste rate is above target and should be reviewed by operations and quality teams.")
else:
    summary_messages.append("✅ Waste rate appears under control.")

if kpis["defect_rate"] > 2:
    summary_messages.append("⚠️ Defect rate is elevated and may indicate quality or supplier issues.")
else:
    summary_messages.append("✅ Defect rate appears acceptable.")

if kpis["delayed"] > 0:
    summary_messages.append("⚠️ Delivery delays detected. Logistics performance should be monitored.")
else:
    summary_messages.append("✅ No major delivery delay issue detected.")

for msg in summary_messages:
    if "⚠️" in msg:
        st.warning(msg)
    else:
        st.success(msg)

st.markdown("---")

# -----------------------------
# PRODUCTION VS SALES
# -----------------------------
st.subheader("🏭 Production vs Sales Performance")

product_summary = df.groupby("product_name")[[
    "quantity_produced",
    "quantity_sold",
    "waste_quantity"
]].sum().reset_index()

fig = px.bar(
    product_summary,
    x="product_name",
    y=["quantity_produced", "quantity_sold"],
    barmode="group",
    title="Production vs Sales by Product"
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# WASTE ANALYSIS
# -----------------------------
st.subheader("♻️ Waste Analysis")

fig_waste = px.bar(
    product_summary.sort_values("waste_quantity", ascending=False),
    x="product_name",
    y="waste_quantity",
    title="Waste Quantity by Product"
)
st.plotly_chart(fig_waste, use_container_width=True)

top_waste_product = product_summary.sort_values("waste_quantity", ascending=False).iloc[0]

st.info(
    f"Highest waste product: **{top_waste_product['product_name']}** "
    f"with **{top_waste_product['waste_quantity']:,.0f}** units/kg waste."
)

# -----------------------------
# SUPPLIER QUALITY
# -----------------------------
st.subheader("🏭 Supplier Quality Performance")

supplier_summary = df.groupby("supplier")[[
    "waste_quantity",
    "defect_count"
]].sum().reset_index()

supplier_summary["supplier_risk_score"] = (
    supplier_summary["waste_quantity"] * 0.4
    + supplier_summary["defect_count"] * 0.6
)

fig_supplier = px.bar(
    supplier_summary.sort_values("supplier_risk_score", ascending=False),
    x="supplier",
    y=["waste_quantity", "defect_count"],
    barmode="group",
    title="Supplier Waste and Defects"
)
st.plotly_chart(fig_supplier, use_container_width=True)

top_supplier_risk = supplier_summary.sort_values("supplier_risk_score", ascending=False).iloc[0]

st.warning(
    f"Supplier requiring attention: **{top_supplier_risk['supplier']}** "
    f"with the highest combined waste/defect risk."
)

# -----------------------------
# REVENUE TREND
# -----------------------------
if "date" in df.columns and "revenue" in df.columns:
    st.subheader("📈 Revenue Trend")

    df["date"] = df["date"].astype(str)

    revenue_trend = (
        df.groupby("date")["revenue"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    fig_revenue = px.line(
        revenue_trend,
        x="date",
        y="revenue",
        title="Revenue Trend Over Time",
        markers=True
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# -----------------------------
# EXECUTIVE RECOMMENDATIONS
# -----------------------------
st.markdown("---")
st.subheader("🎯 Executive Recommendations")

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
    st.write(f"- {rec}")
