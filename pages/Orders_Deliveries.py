import streamlit as st
import plotly.express as px
from data_utils import load_data

st.set_page_config(page_title="Orders & Deliveries", layout="wide")

st.title("📦 Orders & Deliveries — Logistics Monitoring")

df = load_data()

delayed_df = df[df["delivery_status"] == "Delayed"]

c1, c2, c3 = st.columns(3)
c1.metric("Total Orders", len(df))
c2.metric("Delayed Deliveries", len(delayed_df))
c3.metric("Avg Delay Days", f"{df['delivery_delay_days'].mean():.2f}")

delivery_counts = df["delivery_status"].value_counts().reset_index()
delivery_counts.columns = ["Delivery Status", "Count"]

fig = px.pie(
    delivery_counts,
    names="Delivery Status",
    values="Count",
    title="Delivery Status Distribution",
    hole=0.4
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Delayed Deliveries")

st.dataframe(
    delayed_df[[
        "date",
        "customer",
        "product_name",
        "order_quantity",
        "delivery_status",
        "delivery_delay_days"
    ]],
    use_container_width=True
)
