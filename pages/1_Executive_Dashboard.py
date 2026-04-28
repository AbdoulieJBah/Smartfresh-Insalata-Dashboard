import streamlit as st
import plotly.express as px
from data_utils import load_data, calculate_kpis

st.set_page_config(page_title="Executive Dashboard", layout="wide")

st.title("📊 Executive Dashboard — Operations Overview")

df = load_data()
kpis = calculate_kpis(df)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Production", f"{kpis['total_production']:,}")
c2.metric("Total Sales", f"{kpis['total_sales']:,}")
c3.metric("Waste Rate", f"{kpis['waste_rate']:.2f}%")
c4.metric("Revenue", f"€{kpis['revenue']:,.2f}")

c5, c6, c7 = st.columns(3)
c5.metric("Total Waste", f"{kpis['total_waste']:,}")
c6.metric("Delayed Deliveries", kpis["delayed"])
c7.metric("Defect Rate", f"{kpis['defect_rate']:.2f}%")

st.markdown("---")

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

fig_waste = px.bar(
    product_summary.sort_values("waste_quantity", ascending=False),
    x="product_name",
    y="waste_quantity",
    title="Waste by Product"
)

st.plotly_chart(fig_waste, use_container_width=True)
