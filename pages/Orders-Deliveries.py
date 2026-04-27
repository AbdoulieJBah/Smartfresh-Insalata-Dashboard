import streamlit as st
import plotly.express as px
from data_utils import load_data

st.title("📦 Orders & Deliveries")

df = load_data()

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

delayed_df = df[df["delivery_status"] == "Delayed"]

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
