import streamlit as st
import pandas as pd
from data_utils import generate_sample_data
from database import init_db, authenticate_user

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="SmartFresh AI",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# INIT DATABASE
# -----------------------------
init_db()

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

.login-card {
    max-width: 460px;
    margin: 60px auto;
    padding: 30px;
    border-radius: 22px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.role-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: #ecfdf5;
    color: #166534;
    font-weight: 700;
    font-size: 0.82rem;
    margin-top: 8px;
}

.main > div {
    padding-bottom: 50px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION DEFAULTS
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# HIDE SIDEBAR BEFORE LOGIN
# -----------------------------
if not st.session_state.authenticated:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

# -----------------------------
# LOGIN SCREEN
# -----------------------------
if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-card">
        <div style="font-size:2rem; font-weight:850; color:#14532d; text-align:center;">
            🥬 SmartFresh AI
        </div>
        <div style="font-size:1rem; color:#64748b; text-align:center; margin-top:8px;">
            Operations Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    login_col1, login_col2, login_col3 = st.columns([1, 2, 1])

    with login_col2:
        st.subheader("Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            user = authenticate_user(email, password)

            if user and user["status"] == "Active":
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid email or password")

        with st.expander("Demo users"):
            st.write("**Admin:** admin@smartfresh.ai / admin123")
            st.write("**Manager:** manager@smartfresh.ai / manager123")
            st.write("**Operations:** operations@smartfresh.ai / operations123")
            st.write("**Quality:** quality@smartfresh.ai / quality123")
            st.write("**Logistics:** logistics@smartfresh.ai / logistics123")

    st.stop()

# -----------------------------
# USER CONTEXT
# -----------------------------
current_user = st.session_state.user
user_role = current_user["role"]
user_email = current_user["email"]

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.markdown(f"""
<div class="sidebar-header">
    <div class="sidebar-title">🥬 SmartFresh AI</div>
    <div class="sidebar-subtitle">Insalata Operations Platform</div>
    <div class="role-badge">{user_role}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.write(f"👤 {current_user['name']}")
st.sidebar.caption(user_email)

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

if user_role in ["Admin", "Manager"]:
    st.sidebar.markdown("""
    <div class="sidebar-section">Strategic Layer</div>
    <div class="sidebar-item">📊 Executive Dashboard</div>
    <div class="sidebar-item">📈 Business Intelligence</div>
    """, unsafe_allow_html=True)

if user_role in ["Admin", "Manager", "Operations", "Logistics"]:
    st.sidebar.markdown("""
    <div class="sidebar-section">Operations Layer</div>
    <div class="sidebar-item">🥬 Operations Control</div>
    """, unsafe_allow_html=True)

if user_role in ["Admin", "Manager", "Operations"]:
    st.sidebar.markdown("""
    <div class="sidebar-section">Planning Layer</div>
    <div class="sidebar-item">🏭 ERP Production Planner</div>
    """, unsafe_allow_html=True)

if user_role in ["Admin", "Manager", "Operations", "Quality"]:
    st.sidebar.markdown("""
    <div class="sidebar-section">AI Assistant Layer</div>
    <div class="sidebar-item">🤖 AI Copilot</div>
    """, unsafe_allow_html=True)

if user_role in ["Admin", "Manager"]:
    st.sidebar.markdown("""
    <div class="sidebar-section">AI Control Layer</div>
    <div class="sidebar-item">🧠 AI Production Agent</div>
    """, unsafe_allow_html=True)

if user_role in ["Admin", "Manager", "Operations", "Quality", "Logistics"]:
    st.sidebar.markdown("""
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
        ML-driven risk prediction, autonomous AI agents, FastAPI backend scoring,
        Slack/email notifications, and real-time streaming simulation.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# USER ACCESS SUMMARY
# -----------------------------
st.subheader("👤 User Workspace")

u1, u2, u3 = st.columns(3)
u1.metric("Logged In As", current_user["name"])
u2.metric("Role", user_role)
u3.metric("Account Status", current_user["status"])

st.info(
    "Use the sidebar to access the modules available for your role. "
    "SmartFresh AI supports business intelligence, operations control, ERP planning, "
    "AI copilot assistance, autonomous agent monitoring, and task tracking."
)

# -----------------------------
# DATA LAYER
# -----------------------------
st.subheader("📁 Data Layer")

uploaded_file = st.file_uploader(
    "Upload dataset",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.smartfresh_df = pd.read_csv(uploaded_file)
    else:
        st.session_state.smartfresh_df = pd.read_excel(uploaded_file)

    st.success("Dataset loaded successfully")

elif "smartfresh_df" not in st.session_state:
    try:
        st.session_state.smartfresh_df = pd.read_csv("smartfresh_insalata_real_workflow_dataset.csv")
        st.info("Using SmartFresh dataset from repository")
    except Exception:
        st.session_state.smartfresh_df = generate_sample_data()
        st.warning("Default dataset not found — using generated sample data")

# -----------------------------
# PLATFORM OVERVIEW
# -----------------------------
st.markdown("""
### 🚀 Platform Overview

SmartFresh AI is a full-stack operations intelligence system that:

- Monitors production, inventory, quality, and logistics
- Detects operational risks using rules and Machine Learning
- Predicts batch-level risk using an XGBoost-style ML pipeline
- Explains revenue changes and business impact
- Converts insights into trackable actions
- Sends Slack and email alerts for critical issues
- Supports multi-user role-based access
- Simulates Kafka-style live event streaming for real-time monitoring

👉 This transforms dashboards into **AI-driven decision systems**.
""")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")

st.markdown("### 🥬 SmartFresh AI • Built by Abdoulie J Bah")
st.caption("AI Engineer • Data Scientist • Business Intelligence Developer")

c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    b1, b2, b3 = st.columns(3)

    with b1:
        st.link_button("LinkedIn", "https://www.linkedin.com/in/abdoulie-j-bah-b71263244")

    with b2:
        st.link_button("GitHub", "https://github.com/AbdoulieJBah/Smartfresh-Insalata-Dashboard")

    with b3:
        st.link_button("Contact", "mailto:21722285bah@gmail.com")
