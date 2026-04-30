import streamlit as st
import pandas as pd
from data_utils import generate_sample_data
from database import init_db

# -----------------------------
# INIT DATABASE (VERY IMPORTANT)
# -----------------------------
init_db()

st.set_page_config(
    page_title="SmartFresh AI",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# CUSTOM STYLE
# -----------------------------
st.markdown("""
<style>
section[data-testid="stSidebarNav"] { display: none; }

.stApp { background: #f8fafc; }

[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
}

.sidebar-header {
    padding: 14px 10px 18px 10px;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 16px;
}

.sidebar-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #14532d;
}

.sidebar-subtitle {
    font-size: 0.85rem;
    color: #64748b;
}

.sidebar-section {
    font-size: 0.78rem;
    text-transform: uppercase;
    color: #64748b;
    font-weight: 700;
    margin: 18px 0 8px 0;
}

.sidebar-item {
    padding: 9px 10px;
    border-radius: 10px;
    margin-bottom: 6px;
    color: #1f2937;
    font-weight: 600;
    background: #f8fafc;
    border: 1px solid #eef2f7;
}

.sidebar-item:hover {
    background: #ecfdf5;
    border-color: #bbf7d0;
}

/* Hero */
.hero-card {
    padding: 36px;
    border-radius: 24px;
    background: linear-gradient(135deg, #ecfdf5, #ffffff);
    border: 1px solid #bbf7d0;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
}

.hero-title {
    font-size: 44px;
    font-weight: 850;
    color: #14532d;
}

.hero-subtitle {
    font-size: 18px;
    color: #334155;
    line-height: 1.65;
}

/* Footer spacing fix */
.main > div {
    padding-bottom: 50px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR (UPDATED)
# -----------------------------
st.sidebar.markdown("""
<div class="sidebar-header">
    <div class="sidebar-title">🥬 SmartFresh AI</div>
    <div class="sidebar-subtitle">Insalata Operations Platform</div>
</div>

<div class="sidebar-section">Strategic Layer</div>
<div class="sidebar-item">📊 Executive Dashboard</div>
<div class="sidebar-item">📈 Business Intelligence</div>

<div class="sidebar-section">Operations Layer</div>
<div class="sidebar-item">🥬 Operations Control</div>
<div class="sidebar-item">🏭 ERP Production Planner</div>

<div class="sidebar-section">AI Layer</div>
<div class="sidebar-item">🤖 AI Copilot</div>
<div class="sidebar-item">🧠 AI Production Agent</div>

<div class="sidebar-section">Execution Layer</div>
<div class="sidebar-item">📋 Agent Actions</div>
""", unsafe_allow_html=True)

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero-card">
    <div class="hero-title">🥬 SmartFresh AI</div>
    <div class="hero-subtitle">
        End-to-end operations intelligence platform combining business intelligence,
        AI-driven risk detection, and action tracking to support real production decisions.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# DATA LAYER
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload dataset",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.smartfresh_df = pd.read_csv(uploaded_file)
    else:
        st.session_state.smartfresh_df = pd.read_excel(uploaded_file)

    st.success("Dataset loaded")

elif "smartfresh_df" not in st.session_state:
    try:
        st.session_state.smartfresh_df = pd.read_csv("smartfresh_dataset_v2.csv")
        st.info("Using SmartFresh dataset v2")
    except:
        st.session_state.smartfresh_df = generate_sample_data()
        st.warning("Using generated sample data")

# -----------------------------
# PLATFORM OVERVIEW
# -----------------------------
st.markdown("""
### 🚀 Platform Overview

SmartFresh AI is a full-stack operations intelligence system that:

- Monitors production, inventory, and logistics
- Detects operational risks in real time
- Explains revenue changes and business impact
- Predicts future performance risks
- Converts insights into trackable actions

👉 This transforms dashboards into **decision systems**
""")

# -----------------------------
# FOOTER (CLEAN + SAFE)
# -----------------------------
st.markdown("---")

st.markdown("### 🥬 SmartFresh AI • Abdoulie J Bah")
st.caption("AI Engineer • Data Scientist • BI Developer")

c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    b1, b2, b3 = st.columns(3)

    with b1:
        st.link_button("LinkedIn", "https://www.linkedin.com/in/abdoulie-j-bah-b71263244")

    with b2:
        st.link_button("GitHub", "https://github.com/AbdoulieJBah/Smartfresh-Insalata-Dashboard")

    with b3:
        st.link_button("Contact", "mailto:21722285bah@gmail.com")
