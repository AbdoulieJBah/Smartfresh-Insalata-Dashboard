import streamlit as st
import pandas as pd
import plotly.express as px
from data_utils import load_data

st.set_page_config(page_title="Operations Control", layout="wide")

st.title("🥬 Operations Control — Inventory, Expiry & Deliveries")

df = load_data()
df.columns = df.columns.str.strip().str.lower()

# -----------------------------
# SAFETY CHECKS / COLUMN FIXES
# -----------------------------
today = pd.Timestamp.today().normalize()

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

if "expiry_date" not in df.columns:
    if "date" in df.columns:
        df["expiry_date"] = df["date"] + pd.Timedelta(days=5)
    else:
        df["expiry_date"] = today + pd.Timedelta(days=5)
else:
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

df["days_to_expiry"] = (df["expiry_date"] - today).dt.days

if "delivery_status" not in df.columns:
    df["delivery_status"] = "Unknown"

df["delivery_status"] = df["delivery_status"].astype(str).str.strip().str.title()

if "stock_remaining" not in df.columns:
    df["stock_remaining"] = 0

if "product_name" not in df.columns:
    df["product_name"] = "Unknown Product"

# -----------------------------
# FILTERS
# -----------------------------
near_expiry = df[df["days_to_expiry"] <= 2]
expired = df[df["days_to_expiry"] < 0]
delayed_df = df[df["delivery_status"] == "Delayed"]

# -----------------------------
# KPIs
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Stock", f"{df['stock_remaining'].sum():,}")
c2.metric("Near Expiry", len(near_expiry))
c3.metric("Expired Records", len(expired))
c4.metric("Delayed Deliveries", len(delayed_df))

st.markdown("---")

# -----------------------------
# INVENTORY & EXPIRY
# -----------------------------
st.subheader("📦 Inventory & Expiry Monitoring")

inventory_cols = [
    "batch_id",
    "product_name",
    "supplier",
    "stock_remaining",
    "expiry_date",
    "days_to_expiry"
]

inventory_cols = [c for c in inventory_cols if c in df.columns]

st.dataframe(
    df[inventory_cols].sort_values("days_to_expiry"),
    use_container_width=True
)

st.subheader("⚠️ Products Near Expiry")

if len(near_expiry) > 0:
    st.dataframe(
        near_expiry[inventory_cols].sort_values("days_to_expiry"),
        use_container_width=True
    )
else:
    st.success("✅ No products near expiry.")

st.markdown("---")

# -----------------------------
# DELIVERY MONITORING
# -----------------------------
st.subheader("🚚 Delivery Monitoring")

delivery_counts = df["delivery_status"].value_counts().reset_index()
delivery_counts.columns = ["Delivery Status", "Count"]

fig_delivery = px.pie(
    delivery_counts,
    names="Delivery Status",
    values="Count",
    title="Delivery Status Distribution",
    hole=0.4
)

st.plotly_chart(fig_delivery, use_container_width=True)

delivery_cols = [
    "date",
    "client",
    "customer",
    "product_name",
    "order_quantity",
    "delivery_status",
    "delivery_delay_days"
]

delivery_cols = [c for c in delivery_cols if c in df.columns]

st.subheader("Delayed Deliveries")

if len(delayed_df) > 0:
    st.dataframe(
        delayed_df[delivery_cols],
        use_container_width=True
    )
else:
    st.success("✅ No delayed deliveries found.")

st.markdown("---")

# -----------------------------
# STOCK BY PRODUCT
# -----------------------------
st.subheader("📊 Stock by Product")

stock_product = (
    df.groupby("product_name")["stock_remaining"]
    .sum()
    .reset_index()
    .sort_values("stock_remaining", ascending=False)
)

fig_stock = px.bar(
    stock_product,
    x="product_name",
    y="stock_remaining",
    title="Stock Remaining by Product"
)

st.plotly_chart(fig_stock, use_container_width=True)