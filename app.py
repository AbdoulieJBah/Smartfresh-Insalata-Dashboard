import streamlit as st
import pandas as pd
from data_utils import generate_sample_data

st.set_page_config(
    page_title="SmartFresh AI",
    layout="wide"
)

st.markdown("""
<style>
.hero-card {
    padding: 32px;
    border-radius: 22px;
    background: linear-gradient(135deg, #ecfdf5, #ffffff);
    border: 1px solid #bbf7d0;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}
.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #14532d;
    margin-bottom: 10px;
}
.hero-subtitle {
    font-size: 18px;
    color: #334155;
    line-height: 1.6;
}
.feature-card {
    padding: 20px;
    border-radius: 16px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    min-height: 150px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}
.feature-title {
    font-size: 20px;
    font-weight: 700;
    color: #166534;
    margin-bottom: 8px;
}
.feature-text {
    font-size: 15px;
    color: #475569;
    line-height: 1.5;
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
- 💬 Supplier Sentiment Analysis
""")

st.markdown("""
<div class="hero-card">
    <div class="hero-title">🥬 SmartFresh AI</div>
    <div class="hero-subtitle">
        A full-stack operations intelligence platform for Insalata dell’Orto, designed to monitor
        production, inventory, waste, quality, expiry risk, deliveries, traceability, and AI-powered insights.
    </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Executive Dashboard</div>
        <div class="feature-text">
            Monitor production, sales, waste rate, revenue, stock levels, defects, and delivery performance.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🥬 Inventory & Expiry</div>
        <div class="feature-text">
            Track stock, expiry dates, near-expiry products, and batches requiring urgent attention.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🤖 AI Copilot</div>
        <div class="feature-text">
            Ask natural-language questions and generate operational insights using AI and backend risk scoring.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 🚀 Platform Overview")

st.markdown("""
SmartFresh AI helps fresh produce companies transform operational data into actionable intelligence.

It supports:

- Waste reduction and stock optimization
- Inventory and expiry monitoring
- Supplier quality analysis
- Delivery tracking and delay detection
- Batch traceability
- AI-powered operational decision support
- FastAPI backend risk scoring
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
