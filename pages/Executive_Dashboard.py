import streamlit as st
import plotly.express as px
from data_utils import load_data

st.title("📊 Executive Dashboard")

df = load_data()

total_production = df["quantity_produced"].sum()
total_sales = df["quantity_sold"].sum()
total_waste = df["waste_quantity"].sum()
waste_rate = (total_waste / total_production) * 100
revenue = df["revenue"].sum()
delayed = (df["delivery_status"] == "Delayed").sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Production", f"{total_production:,}")
k2.metric("Total Sales", f"{total_sales:,}")
k3.metric("Waste Rate", f"{waste_rate:.2f}%")
k4.metric("Revenue", f"€{revenue:,.2f}")

k5, k6 = st.columns(2)
k5.metric("Total Waste", f"{total_waste:,}")
k6.metric("Delayed Deliveries", delayed)

product_summary = df.groupby("product_name")[["quantity_produced", "quantity_sold", "waste_quantity"]].sum().reset_index()

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
