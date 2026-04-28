import streamlit as st
import pandas as pd
from data_utils import generate_sample_data

st.set_page_config(
    page_title="SmartFresh AI",
    layout="wide"
)

# -----------------------------
# CUSTOM STYLE
# -----------------------------

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc, #ecfdf5);
}

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

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🥬 SmartFresh AI")
st.sidebar.caption("Insalata dell’Orto Platform")

st.sidebar.markdown("""
### Operations Intelligence

- 📊 Executive Dashboard  
- 🥬 Operations Control  
- ✅ Quality & Sentiment  
- 🔎 Traceability & Risk  
- 🏭 ERP Production Planner  
- 🤖 AI Copilot  
- 🧠 AI Production Agent
""")

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero-card">
    <div class="hero-title">🥬 SmartFresh AI</div>
    <div class="hero-subtitle">
        A full-stack operations intelligence platform for fresh produce companies.
        Monitor production, inventory, waste, quality, expiry risk, deliveries, traceability,
        AI insights, and ERP-style production planning.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# FEATURE CARDS
# -----------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Operations Intelligence</div>
        <div class="feature-text">
            Track production, sales, stock, waste, delivery delays, quality, and supplier performance.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🏭 ERP Production Planning</div>
        <div class="feature-text">
            Optimize machines, shifts, production time, pallets, incoming cases, and departure deadlines.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🤖 AI Copilot</div>
        <div class="feature-text">
            Ask questions, run real production tools, and generate operational recommendations.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# DATA UPLOAD / DEFAULT DATA
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Insalata CSV/Excel dataset",
    type=["csv", "xlsx"],
    key="main_dataset_uploader"
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.smartfresh_df = pd.read_csv(uploaded_file)
    else:
        st.session_state.smartfresh_df = pd.read_excel(uploaded_file)

    st.success("✅ Uploaded dataset loaded successfully")

elif "smartfresh_df" not in st.session_state:
    try:
        st.session_state.smartfresh_df = pd.read_csv("smartfresh_insalata_real_workflow_dataset.csv")
        st.info("ℹ️ Using default SmartFresh dataset from repository")
    except Exception:
        st.session_state.smartfresh_df = generate_sample_data()
        st.warning("⚠️ Default dataset not found — using generated sample data")

# -----------------------------
# PLATFORM OVERVIEW
# -----------------------------
st.markdown("### 🚀 Platform Overview")

st.markdown("""
SmartFresh AI helps fresh produce companies transform operational data into decision-ready intelligence.

It supports:

- Production and sales monitoring
- Inventory and expiry control
- Waste and defect analysis
- Supplier sentiment analysis
- Delivery delay tracking
- Batch traceability and backend risk scoring
- ERP-style production scheduling and shift optimization
- AI-assisted production planning
""")

st.markdown("---")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<div style="text-align:center; margin-top:30px; padding:18px; border-radius:16px; background:linear-gradient(180deg, rgba(30,41,59,0.7), rgba(15,23,42,0.9)); border:1px solid rgba(59,130,246,0.25);">

<div style="font-size:1.05rem; color:#e5e7eb; margin-bottom:6px;">
Built by <strong style="color:#3b82f6;">Abdoulie J Bah</strong> 🚀
</div>

<div style="font-size:0.9rem; color:#94a3b8; margin-bottom:12px;">
AI Engineer • Data Scientist • Business Intelligence Developer
</div>

<div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">

<a href="https://www.linkedin.com/in/abdoulie-j-bah-b71263244" target="_blank" style="text-decoration:none; padding:8px 14px; border-radius:10px; background:#0ea5e9; color:white; font-weight:600;">LinkedIn</a>

<a href="https://github.com/AbdoulieJBah/Smartfresh-Insalata-Dashboard/tree/main" target="_blank" style="text-decoration:none; padding:8px 14px; border-radius:10px; background:#1f2937; color:white; font-weight:600; border:1px solid rgba(255,255,255,0.1);">GitHub</a>

<a href="mailto:21722285bah@gmail.com" style="text-decoration:none; padding:8px 14px; border-radius:10px; background:#2563eb; color:white; font-weight:600;">Contact</a>

</div>
</div>
""", unsafe_allow_html=True)
