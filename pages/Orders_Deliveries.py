import streamlit as st
import plotly.express as px
from data_utils import load_data

st.set_page_config(page_title="Orders & Deliveries", layout="wide")

st.title("📦 Orders & Deliveries — Logistics Monitoring")

df = load_data()

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Create missing order_quantity if dataset does not have it
if "order_quantity" not in df.columns and "quantity_sold" in df.columns:
    df["order_quantity"] = df["quantity_sold"]

required_columns = [
    "date",
    "customer",
    "product_name",
    "order_quantity",
    "delivery_status",
    "delivery_delay_days"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.write("Available columns:", list(df.columns))
    st.stop()

# Normalize delivery status values
df["delivery_status"] = df["delivery_status"].astype(str).str.strip().str.title()

delayed_df = df[df["delivery_status"] == "Delayed"]

avg_delay = df["delivery_delay_days"].mean()

c1, c2, c3 = st.columns(3)
c1.metric("Total Orders", len(df))
c2.metric("Delayed Deliveries", len(delayed_df))
c3.metric("Avg Delay Days", f"{avg_delay:.2f}")

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

if len(delayed_df) > 0:
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
else:
    st.success("✅ No delayed deliveries found.")
