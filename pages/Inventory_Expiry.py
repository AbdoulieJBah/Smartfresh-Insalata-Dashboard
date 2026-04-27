import streamlit as st
import pandas as pd
from datetime import datetime
from data_utils import load_data

st.set_page_config(page_title="Inventory & Expiry", layout="wide")

st.title("🥬 Inventory & Expiry — Stock Monitoring")

df = load_data()
today = pd.Timestamp(datetime.today().date())

df["days_to_expiry"] = (df["expiry_date"] - today).dt.days

near_expiry = df[df["days_to_expiry"] <= 2]
expired = df[df["days_to_expiry"] < 0]

c1, c2, c3 = st.columns(3)
c1.metric("Total Stock", f"{df['stock_remaining'].sum():,}")
c2.metric("Near Expiry", len(near_expiry))
c3.metric("Expired Records", len(expired))

st.subheader("Inventory Overview")

st.dataframe(
    df[[
        "batch_id",
        "product_name",
        "supplier",
        "stock_remaining",
        "expiry_date",
        "days_to_expiry"
    ]].sort_values("days_to_expiry"),
    use_container_width=True
)

st.subheader("⚠️ Products Near Expiry")

st.dataframe(
    near_expiry[[
        "batch_id",
        "product_name",
        "stock_remaining",
        "expiry_date",
        "supplier"
    ]],
    use_container_width=True
)
