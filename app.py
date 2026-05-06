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
    background:
        radial-gradient(circle at top left, rgba(34,197,94,0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(59,130,246,0.10), transparent 25%),
        linear-gradient(135deg, #020403 0%, #050807 45%, #07130c 100%);
    color: #e5e7eb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06120d 0%, #081b12 65%, #020403 100%);
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
    position: relative;
    overflow: hidden;
    padding: 48px;
    border-radius: 32px;
    background:
        linear-gradient(135deg, rgba(15,23,42,0.98), rgba(6,78,59,0.82)),
        radial-gradient(circle at top right, rgba(34,197,94,0.32), transparent 38%);
    border: 1px solid rgba(34,197,94,0.45);
    box-shadow: 0 26px 70px rgba(0,0,0,0.48);
}

.hero-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(34,197,94,0.16);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.35);
    font-weight: 850;
    font-size: 0.78rem;
    margin-bottom: 14px;
}

.hero-title {
    font-size: 52px;
    font-weight: 950;
    color: #ffffff;
    letter-spacing: -0.04em;
    line-height: 1.05;
}

.hero-title span {
    color: #86efac;
}

.hero-subtitle {
    max-width: 1050px;
    font-size: 18px;
    color: #d1d5db;
    line-height: 1.75;
    margin-top: 16px;
}

.section-title {
    font-size: 1.35rem;
    font-weight: 950;
    color: #ffffff;
    margin: 2rem 0 1rem 0;
}

.premium-card {
    padding: 24px;
    border-radius: 20px;
    background: rgba(15,23,42,0.86);
    border: 1px solid rgba(34,197,94,0.25);
    box-shadow: 0 14px 36px rgba(0,0,0,0.30);
    min-height: 150px;
}

.premium-card:hover {
    border-color: rgba(34,197,94,0.55);
    box-shadow: 0 0 26px rgba(34,197,94,0.12);
}

.card-label {
    color: #9ca3af;
    font-size: 0.82rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.card-value {
    color: #ffffff;
    font-size: 1.75rem;
    font-weight: 900;
    margin-top: 10px;
}

.card-delta {
    color: #86efac;
    font-size: 0.86rem;
    margin-top: 8px;
    line-height: 1.55;
}

.module-card {
    padding: 22px;
    border-radius: 20px;
    background: rgba(15,23,42,0.84);
    border: 1px solid rgba(34,197,94,0.22);
    box-shadow: 0 14px 34px rgba(0,0,0,0.30);
    min-height: 180px;
    margin-bottom: 14px;
}

.module-title {
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 900;
    margin-bottom: 10px;
}

.module-text {
    color: #d1d5db;
    font-size: 0.92rem;
    line-height: 1.65;
}

.stack-pill {
    display: inline-block;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(34,197,94,0.13);
    color: #bbf7d0;
    border: 1px solid rgba(34,197,94,0.28);
    margin: 5px 4px;
    font-weight: 750;
    font-size: 0.82rem;
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


def section_title(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def module_card(title, text):
    st.markdown(f"""
    <div class="module-card">
        <div class="module-title">{title}</div>
        <div class="module-text">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def stack_pills(items):
    html = "".join([f'<span class="stack-pill">{item}</span>' for item in items])
    st.markdown(html, unsafe_allow_html=True)

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
    <div class="hero-badge">AI-Powered Industry 4.0 Platform</div>
    <div class="hero-title">🥬 SmartFresh <span>AI</span></div>
    <div class="hero-subtitle">
        A full-stack operations intelligence platform for fresh-produce manufacturing.
        SmartFresh AI combines Business Intelligence, ERP/MES-inspired production planning,
        machine digital twin simulation, ML-driven risk prediction, autonomous AI agents,
        FastAPI backend scoring, Slack/email notifications, and real-time AI control-room monitoring.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# USER ACCESS SUMMARY
# -----------------------------
section_title("👤 User Workspace")

u1, u2, u3 = st.columns(3)

with u1:
    premium_metric("Logged In As", current_user["name"], "Authenticated user")

with u2:
    premium_metric("Role", user_role, "Role-based access enabled")

with u3:
    premium_metric("Account Status", current_user["status"], "Active workspace")

st.info(
    "Use the sidebar to access modules available for your role. The system supports BI, ERP planning, "
    "MES-style operator workflow, Digital Twin simulation, AI Copilot assistance, autonomous agent monitoring, "
    "FastAPI backend risk scoring, and action tracking."
)

# -----------------------------
# DATA LAYER
# -----------------------------
st.markdown("---")
section_title("📁 Data Layer")

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
section_title("🚀 Platform Overview")

st.markdown("""
<div class="premium-card">
<b>SmartFresh AI</b> is not just a dashboard. It is an AI-driven manufacturing intelligence system
inspired by real fresh-produce operations, ERP/MES environments, machine operator dashboards,
and Industry 4.0 control-room workflows.
<br><br>
It monitors production, inventory, quality, logistics, revenue performance, machine health,
operator activity, and simulated real-time factory signals. It detects risks using rules and
machine learning, converts alerts into actions, supports AI decision-making, and gives leadership
a complete view of operational health.
<br><br>
<span style="color:#86efac;font-weight:800;">
This transforms raw operational data into autonomous business and factory decisions.
</span>
</div>
""", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

with f1:
    premium_metric("AI Decisions", "ML + Agents", "Predict risks and recommend actions")

with f2:
    premium_metric("Industry 4.0", "MES + Machines", "Digital twin and control-room logic")

with f3:
    premium_metric("Automation", "Alerts + Tasks", "Slack/email and action tracking")

with f4:
    premium_metric("Architecture", "Streamlit + FastAPI", "Frontend, API, ML and database layers")

# -----------------------------
# ARCHITECTURE
# -----------------------------
section_title("🏗️ System Architecture")

a1, a2, a3 = st.columns(3)

with a1:
    module_card(
        "📊 Intelligence Layer",
        "Executive dashboards, BI analytics, revenue trends, supplier performance, quality monitoring, and role-based insights."
    )

with a2:
    module_card(
        "🏭 ERP/MES Layer",
        "Production planning, shift optimization, machine allocation, work order logic, operator workflow, and packaging calculations."
    )

with a3:
    module_card(
        "🧠 AI Agent Layer",
        "Autonomous production agent, multi-agent planning, AI recommendations, critical risk escalation, and decision summaries."
    )

a4, a5, a6 = st.columns(3)

with a4:
    module_card(
        "⚙️ Machine Layer",
        "Digital twin simulation, live machine signals, risk score, OEE, speed, downtime, vibration, reject rate, and alarms."
    )

with a5:
    module_card(
        "🌐 Backend API Layer",
        "FastAPI backend risk scoring, alert retrieval, action updates, stream event feed, and service health endpoints."
    )

with a6:
    module_card(
        "📡 Streaming Layer",
        "Kafka-style simulated production events for temperature, logistics, inventory, quality, and live operational monitoring."
    )

# -----------------------------
# AI AGENTS
# -----------------------------
section_title("🤖 AI Agent Capabilities")

g1, g2, g3, g4 = st.columns(4)

with g1:
    module_card(
        "BI Agent",
        "Explains revenue, client contribution, product trends, and business performance."
    )

with g2:
    module_card(
        "Operations Agent",
        "Detects production, waste, cold-chain, delivery, and inventory risks."
    )

with g3:
    module_card(
        "Quality Agent",
        "Flags defects, supplier quality issues, temperature breaches, and high-waste products."
    )

with g4:
    module_card(
        "Executive Agent",
        "Summarizes strategic risk and recommends escalation priorities for management."
    )

# -----------------------------
# INDUSTRY 4.0 FEATURES
# -----------------------------
section_title("🏭 Industry 4.0 Features")

i1, i2, i3 = st.columns(3)

with i1:
    premium_metric("OEE Monitoring", "Availability + Performance + Quality", "Manufacturing performance intelligence")

with i2:
    premium_metric("Digital Twin", "Simulated Factory Assets", "Machine risk and operator workflow simulation")

with i3:
    premium_metric("AI Control Room", "Real-Time Decisions", "Machine wall, risk alerts, and escalation banners")

# -----------------------------
# TECH STACK
# -----------------------------
section_title("🧰 Technology Stack")

stack_pills([
    "Python",
    "Streamlit",
    "Pandas",
    "NumPy",
    "Plotly",
    "Scikit-learn",
    "XGBoost",
    "FastAPI",
    "Uvicorn",
    "Pydantic",
    "SQLite",
    "Requests",
    "Google Generative AI",
    "Machine Learning",
    "Digital Twin Simulation",
    "ERP/MES Logic",
    "Industry 4.0",
])

# -----------------------------
# VALUE PROPOSITION
# -----------------------------
section_title("🎯 Project Value Proposition")

v1, v2 = st.columns(2)

with v1:
    st.markdown("""
    <div class="premium-card">
    <b style="color:#ffffff;font-size:1.15rem;">For Manufacturing Operations</b>
    <br><br>
    SmartFresh AI helps operations teams monitor production, inventory, expiry risk,
    machine health, delivery delays, and quality issues from one unified control system.
    <br><br>
    It supports faster decisions, earlier risk detection, and better operational coordination.
    </div>
    """, unsafe_allow_html=True)

with v2:
    st.markdown("""
    <div class="premium-card">
    <b style="color:#ffffff;font-size:1.15rem;">For AI / Data Portfolio</b>
    <br><br>
    This project demonstrates full-stack AI product development: analytics, machine learning,
    backend API design, database integration, role-based access, AI agents, and Industry 4.0 simulation.
    <br><br>
    It is positioned for AI Engineer, Data Scientist, BI Developer, and Digital Transformation roles.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown("### 🥬 SmartFresh AI • Built by Abdoulie J Bah")
st.caption("AI Engineer • Data Scientist • Business Intelligence Developer • Industry 4.0 AI Systems")

c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    b1, b2, b3 = st.columns(3)

    with b1:
        st.link_button("LinkedIn", "https://www.linkedin.com/in/abdoulie-j-bah-b71263244")

    with b2:
        st.link_button("GitHub", "https://github.com/AbdoulieJBah/Smartfresh-Insalata-Dashboard")

    with b3:
        st.link_button("Contact", "mailto:21722285bah@gmail.com")
