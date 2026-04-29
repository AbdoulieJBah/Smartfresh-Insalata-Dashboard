import streamlit as st
import pandas as pd
from data_utils import generate_sample_data

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
/* Hide default Streamlit page navigation */
section[data-testid="stSidebarNav"] {
    display: none;
}

/* Keep app light/system-friendly */
.stApp {
    background: #f8fafc;
}

/* Enterprise sidebar */
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
    margin-bottom: 4px;
}

.sidebar-subtitle {
    font-size: 0.85rem;
    color: #64748b;
}

.sidebar-section {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
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
    margin-bottom: 26px;
}

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    background: #dcfce7;
    color: #166534;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 14px;
}

.hero-title {
    font-size: 44px;
    font-weight: 850;
    color: #14532d;
    margin-bottom: 12px;
    line-height: 1.12;
}

.hero-subtitle {
    font-size: 18px;
    color: #334155;
    line-height: 1.65;
    max-width: 1050px;
}

/* Status banner */
.status-banner {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 24px;
}

.status-pill {
    padding: 10px 14px;
    border-radius: 14px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    font-size: 0.9rem;
    font-weight: 700;
    color: #334155;
}

.status-green {
    color: #166534;
}

/* Feature cards */
.feature-card {
    padding: 22px;
    border-radius: 18px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    min-height: 175px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    transition: all 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
}

.feature-title {
    font-size: 20px;
    font-weight: 800;
    color: #14532d;
    margin-bottom: 10px;
}

.feature-text {
    font-size: 15px;
    color: #475569;
    line-height: 1.55;
}

.overview-card {
    padding: 24px;
    border-radius: 18px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.footer-card {
    text-align: center;
    margin-top: 32px;
    padding: 22px;
    border-radius: 18px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.footer-name {
    font-size: 1.05rem;
    color: #14532d;
    font-weight: 800;
    margin-bottom: 6px;
}

.footer-role {
    font-size: 0.92rem;
    color: #64748b;
    margin-bottom: 14px;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}

.footer-link {
    text-decoration: none;
    padding: 8px 14px;
    border-radius: 10px;
    color: white !important;
    font-weight: 700;
}

@media (max-width: 768px) {
    .hero-card {
        padding: 24px;
        border-radius: 20px;
    }

    .hero-title {
        font-size: 30px;
    }

    .hero-subtitle {
        font-size: 15px;
    }

    .feature-card {
        min-height: auto;
        margin-bottom: 12px;
    }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown("""
<div class="sidebar-header">
    <div class="sidebar-title">🥬 SmartFresh AI</div>
    <div class="sidebar-subtitle">Insalata dell’Orto Operations Platform</div>
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
""", unsafe_allow_html=True)

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero-card">
    <div class="hero-badge">AI-Powered Fresh Produce Operations</div>
    <div class="hero-title">🥬 SmartFresh AI</div>
    <div class="hero-subtitle">
        Unifies production, inventory, quality, and logistics into a single intelligent system—enabling
        real-time monitoring, traceability, risk detection, and AI-driven decision support.
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SYSTEM STATUS
# -----------------------------
st.markdown("""
<div class="status-banner">
    <div class="status-pill"><span class="status-green">●</span> System Status: Operational</div>
    <div class="status-pill"><span class="status-green">●</span> Data Layer: Ready</div>
    <div class="status-pill"><span class="status-green">●</span> AI Layer: Connected</div>
    <div class="status-pill"><span class="status-green">●</span> ERP Planner: Active</div>
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
            Monitor production, sales, stock, waste, quality, expiry risks, delivery delays,
            and supplier performance from one unified view.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🏭 ERP Production Planning</div>
        <div class="feature-text">
            Plan colli, buste, kg, incoming cases, pedane, machines, shifts, and departure deadlines
            with ERP-style scheduling logic.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🧠 AI Decision Layer</div>
        <div class="feature-text">
            Use an AI Copilot for operational questions and an AI Agent for risk detection,
            decision support, and action recommendations.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
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
        st.info("ℹ️ Using default SmartFresh workflow dataset from repository")
    except Exception:
        st.session_state.smartfresh_df = generate_sample_data()
        st.warning("⚠️ Default dataset not found — using generated sample data")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# PLATFORM OVERVIEW
# -----------------------------
st.markdown("""
<div class="overview-card">
<h3>🚀 Platform Overview</h3>

<p>
SmartFresh AI helps fresh produce companies transform raw operational data into actionable,
decision-ready intelligence across production, logistics, quality, and business performance.
</p>

<ul>
<li>Real-time production and sales monitoring</li>
<li>Inventory management and expiry risk control</li>
<li>Waste, defect, and quality performance analysis</li>
<li>Supplier performance and feedback sentiment insights</li>
<li>Delivery tracking and delay risk detection</li>
<li>End-to-end batch traceability and risk scoring</li>
<li>ERP-style production planning, packaging logic, and resource optimization</li>
<li>Shift scheduling and machine allocation optimization</li>
<li>AI-powered Copilot for operational questions and insights</li>
<li>Autonomous AI Agent for risk detection, decision support, and action recommendations</li>
</ul>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<div class="footer-card">
    <div class="footer-name">SmartFresh AI • Built by Abdoulie J Bah 🚀</div>
    <div class="footer-role">AI Engineer • Data Scientist • Business Intelligence Developer</div>

    <div class="footer-links">
        <a class="footer-link" href="https://www.linkedin.com/in/abdoulie-j-bah-b71263244" target="_blank" style="background:#0ea5e9;">LinkedIn</a>
        <a class="footer-link" href="https://github.com/AbdoulieJBah/Smartfresh-Insalata-Dashboard/tree/main" target="_blank" style="background:#111827;">GitHub</a>
        <a class="footer-link" href="mailto:21722285bah@gmail.com" style="background:#16a34a;">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)
