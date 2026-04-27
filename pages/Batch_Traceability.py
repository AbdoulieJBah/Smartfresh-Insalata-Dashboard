import streamlit as st
from data_utils import load_data

st.title("🔎 Batch Traceability")

df = load_data()

selected_batch = st.selectbox(
    "Select Batch ID",
    df["batch_id"].unique()
)

batch_info = df[df["batch_id"] == selected_batch]

st.dataframe(batch_info, use_container_width=True)

if len(batch_info) > 0:
    row = batch_info.iloc[0]

    st.subheader("Batch Details")
    st.write(f"**Product:** {row['product_name']}")
    st.write(f"**Supplier:** {row['supplier']}")
    st.write(f"**Customer:** {row['customer']}")
    st.write(f"**Expiry Date:** {row['expiry_date'].date()}")
    st.write(f"**Delivery Status:** {row['delivery_status']}")
