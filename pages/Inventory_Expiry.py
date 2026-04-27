import streamlit as st
import pandas as pd
from datetime import datetime
from data_utils import load_data

st.title("🥬 Inventory & Expiry")

df = load_data()

today = pd.Timestamp(datetime.today().date())

df["days_to_expiry"] = (df["expiry_date"] - today).dt.days

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

near_expiry = df[df["days_to_expiry"] <= 2]

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
