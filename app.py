import streamlit as st
import pandas as pd
from data_utils import generate_sample_data

st.set_page_config(
    page_title="SmartFresh AI",
    layout="wide"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc, #ecfdf5);
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #14532d;
}

.hero-card {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(135deg, #ecfdf5, #ffffff);
    border: 1px solid #bbf7d0;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🥬 SmartFresh AI")
st.sidebar.caption("Insalata dell’Orto Platform")

st.sidebar.markdown("""
### Operations Intelligence

- 📊 Executive Insights  
- 🥬 Inventory Monitoring  
- ✅ Quality Control  
- 📦 Logistics Tracking  
- 🔎 Batch Traceability  
- 🤖 AI Copilot  
""")

st.markdown("""
<div class="hero-card">
    <div class="main-title">🥬 SmartFresh AI — Insalata dell’Orto Dashboard</div>
    <p style="font-size:18px; color:#334155;">
        Business intelligence system for monitoring production, inventory, waste,
        quality, expiry risk, deliveries, and operational performance.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🚀 Platform Overview")

st.markdown("""
SmartFresh AI helps fresh produce companies transform operational data into actionable insights.

It supports:
- Waste reduction
- Inventory and expiry monitoring
- Supplier quality analysis
- Delivery tracking
- Batch traceability
- AI-powered decision support
""")

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

st.markdown("---")

st.markdown("""
<center>
Built by <b>Abdoulie J Bah</b> 🚀  
<br>
AI Engineer • Data Scientist • Business Intelligence Developer
</center>
""", unsafe_allow_html=True)
