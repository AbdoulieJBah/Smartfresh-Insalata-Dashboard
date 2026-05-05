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
    initial_sidebar_state="expanded"
)

# -----------------------------
# INIT DATABASE
# -----------------------------
init_db()

# -----------------------------
# PREMIUM DARK UI CSS
# -----------------------------
st.markdown("""
<style>
section[data-testid="stSidebarNav"] { display: none; }

.stApp {
    background: radial-gradient(circle at top left, #123524 0%, #050807 35%, #020403 100%);
    color: #e5e7eb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06120d 0%, #081b12 100%);
    border-right: 1px solid rgba(34,197,94,0.25);
}

[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

.sidebar-header {
    padding: 18px 14px;
    border-radius: 18px;
    margin-bottom: 20px;
    background: rgba(17, 24, 39, 0.92);
    border: 1px solid rgba(34,197,94,0.35);
    box-shadow: 0 0 24px rgba(34,197,94,0.12);
}

.sidebar-title {
    font-size: 1.45rem;
    font-weight: 900;
    color: #86efac;
}

.sidebar-subtitle {
    font-size: 0.85rem;
    color: #9ca3af;
}

.sidebar-section {
    font-size: 0.72rem;
    text-transform: uppercase;
    color: #86efac;
    font-weight: 800;
    margin: 20px 0 8px 4px;
    letter-spacing: 0.08em;
}

.sidebar-item {
    padding: 11px 12px;
    border-radius: 12px;
    margin-bottom: 8px;
    color: #e5e7eb;
    font-weight: 650;
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148,163,184,0.15);
}

.sidebar-item:hover {
    background: rgba(22, 101, 52, 0.45);
    border-color: rgba(34,197,94,0.55);
}

.role-badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(34,197,94,0.16);
    color: #86efac;
    font-weight: 800;
    font-size: 0.78rem;
    margin-top: 10px;
    border: 1px solid rgba(34,197,94,0.35);
}

.hero-card {
    padding: 42px;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(15,23,42,0.96), rgba(6,78,59,0.78)),
        radial-gradient(circle at top right, rgba(34,197,94,0.25), transparent 35%);
    border: 1px solid rgba(34,197,94,0.42);
    box-shadow: 0 18px 50px rgba(0,0,0,0.45);
}

.hero-title {
    font-size: 48px;
    font-weight: 950;
    color: #ffffff;
    letter-spacing: -0.03em;
}

.hero-title span {
    color: #86efac;
}

.hero-subtitle {
    max-width: 980px;
    font-size: 18px;
    color: #d1d5db;
    line-height: 1.75;
    margin-top: 14px;
}

.premium-card {
    padding: 22px;
    border-radius: 18px;
    background: rgba(15,23,42,0.86);
    border: 1px solid rgba(34,197,94,0.25);
    box-shadow: 0 12px 30px rgba(0,0,0,0.28);
}

.card-label {
    color: #9ca3af;
    font-size: 0.9rem;
    font-weight: 650;
}

.card-value {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 850;
    margin-top: 8px;
}

.card-delta {
    color: #86efac;
    font-size: 0.85rem;
    margin-top: 6px;
}

.login-card {
    max-width: 520px;
    margin: 70px auto 30px auto;
    padding: 38px;
    border-radius: 28px;
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid rgba(34,197,94,0.35);
    box-shadow: 0 18px 55px rgba(0,0,0,0.45);
    text-align: center;
}

.login-title {
    font-size: 2.35rem;
    font-weight: 950;
    color: #ffffff;
}

.login-title span {
    color: #86efac;
}

.login-subtitle {
    color: #d1d5db;
    margin-top: 8px;
    font-size: 1rem;
}

h1, h2, h3 {
    color: #ffffff !important;
}

div[data-testid="stMetric"] {
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(34,197,94,0.22);
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.25);
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid rgba(34,197,94,0.5);
    background: linear-gradient(135deg, #16a34a, #15803d);
    color: white;
    font-weight: 700;
}

.stButton > button:hover {
    border-color: #86efac;
    box-shadow: 0 0 18px rgba(34,197,94,0.3);
}

div[data-testid="stAlert"] {
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def premium_metric(label, value, delta=""):
    st.markdown(f"""
    <div class="premium-card">
        <div class="card-label">{label}</div>
        <div class="card-value">{value}</div>
        <div class="card-delta">{delta}</div>
    </div>
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
        <div class="login-title">🥬 SmartFresh <span>AI</span></div>
        <div class="login-subtitle">Industry 4.0 Operations Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    login_col1, login_col2, login_col3 = st.columns([1.2, 1.6, 1.2])

    with login_col2:
        st.subheader("Login")

        email = st.text_input("Email", placeholder="admin@smartfresh.ai")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        if st.button("Login", use_container_width=True):
            clean_email = email.strip().lower()
            user = authenticate_user(clean_email, password)

            if user and str(user.get("status", "")).lower() == "active":
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

if st.sidebar.button("Logout", use_container_width=True):
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

if user_role in ["Admin", "Manager", "Operations", "Quality", "Logistics"]:
    st.sidebar.markdown("""
    <div class="sidebar-section">Industry 4.0 Layer</div>
    <div class="sidebar-item">🏭 Machine Digital Twin</div>
    <div class="sidebar-item">🧠 AI Control Room</div>
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
    <div class="hero-title">🥬 SmartFresh <span>AI</span></div>
    <div class="hero-subtitle">
        AI-powered Industry 4.0 operations intelligence platform combining business intelligence,
        ERP/MES-inspired workflows, machine digital twin simulation, ML-driven risk prediction,
        autonomous AI agents, FastAPI backend scoring, Slack/email notifications, and real-time
        production control-room intelligence.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# USER ACCESS SUMMARY
# -----------------------------
st.subheader("👤 User Workspace")

u1, u2, u3 = st.columns(3)

with u1:
    premium_metric("Logged In As", current_user["name"], "Authenticated user")

with u2:
    premium_metric("Role", user_role, "Role-based access enabled")

with u3:
    premium_metric("Account Status", current_user["status"], "Active workspace")

st.info(
    "Use the sidebar to access the modules available for your role. "
    "SmartFresh AI supports business intelligence, operations control, ERP planning, "
    "AI copilot assistance, machine digital twin simulation, AI control-room monitoring, "
    "autonomous agent monitoring, and task tracking."
)

# -----------------------------
# DATA LAYER
# -----------------------------
st.markdown("---")
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
        st.success("Using SmartFresh dataset from repository")
    except Exception:
        st.session_state.smartfresh_df = generate_sample_data()
        st.warning("Default dataset not found — using generated sample data")

# -----------------------------
# PLATFORM OVERVIEW
# -----------------------------
st.markdown("---")
st.subheader("🚀 Platform Overview")

st.markdown("""
<div class="premium-card">
<b>SmartFresh AI</b> is a full-stack AI operations intelligence system inspired by real fresh-produce
production workflows, ERP/MES environments, and shop-floor machine data.
<br><br>
It monitors production, inventory, quality, logistics, revenue performance, machine health,
operator workflows, and simulated real-time factory signals.
<br><br>
The platform detects operational risks using rules and Machine Learning, predicts batch-level
and machine-level risk, converts insights into trackable actions, sends Slack/email alerts,
and simulates Kafka-style live event streaming for real-time monitoring.
<br><br>
<span style="color:#86efac;font-weight:800;">
This transforms dashboards into an AI-driven Industry 4.0 decision system.
</span>
</div>
""", unsafe_allow_html=True)

st.markdown("")

f1, f2, f3, f4 = st.columns(4)

with f1:
    premium_metric("AI Decisions", "ML + Agents", "Risk prediction & actions")

with f2:
    premium_metric("Industry 4.0", "MES + Machines", "Digital twin simulation")

with f3:
    premium_metric("Automation", "Slack + Email", "Critical alerts")

with f4:
    premium_metric("Architecture", "Streamlit + FastAPI", "Production-ready layers")

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
