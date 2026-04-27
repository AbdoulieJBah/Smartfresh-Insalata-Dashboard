import streamlit as st
import pandas as pd
from data_utils import generate_sample_data

st.set_page_config(
    page_title="SmartFresh AI",
    layout="wide"
)

st.title("🥬 SmartFresh AI — Insalata dell’Orto Dashboard")

st.write(
    "Business intelligence system for monitoring production, inventory, waste, quality, expiry risk, and deliveries."
)

uploaded_file = st.file_uploader(
    "Upload Insalata CSV/Excel dataset",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.smartfresh_df = pd.read_csv(uploaded_file)
    else:
        st.session_state.smartfresh_df = pd.read_excel(uploaded_file)

    st.success("✅ Uploaded dataset loaded successfully")
else:
    if "smartfresh_df" not in st.session_state:
        st.session_state.smartfresh_df = generate_sample_data()
        st.info("ℹ️ Using sample Insalata dell’Orto dataset")

st.sidebar.title("🥬 SmartFresh AI")
st.sidebar.caption("Insalata dell’Orto Operations Dashboard")

st.sidebar.markdown("""
Operations Intelligence Platform

- 📊 Executive Insights
- 🥬 Inventory Monitoring
- ✅ Quality Control
- 📦 Logistics Tracking
- 🔎 Traceability
""")
