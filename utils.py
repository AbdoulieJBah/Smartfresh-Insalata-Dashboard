import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    /* -----------------------------
       GLOBAL APP BACKGROUND
    ----------------------------- */
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(34,197,94,0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(16,185,129,0.10), transparent 25%),
            linear-gradient(135deg, #020403 0%, #050807 45%, #07130c 100%) !important;
        color: #f8fafc !important;
    }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        max-width: 1280px;
    }

    /* -----------------------------
       SIDEBAR
    ----------------------------- */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #06120d 0%, #081b12 55%, #020403 100%) !important;
        border-right: 1px solid rgba(34,197,94,0.28);
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    section[data-testid="stSidebarNav"] {
        display: none;
    }

    /* -----------------------------
       TEXT
    ----------------------------- */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        letter-spacing: -0.02em;
    }

    p, span, label, div {
        font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    /* -----------------------------
       PREMIUM HERO CARD
    ----------------------------- */
    .premium-hero {
        padding: 34px 38px;
        border-radius: 28px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.98), rgba(6,78,59,0.78)),
            radial-gradient(circle at top right, rgba(34,197,94,0.26), transparent 38%);
        border: 1px solid rgba(34,197,94,0.42);
        box-shadow:
            0 22px 60px rgba(0,0,0,0.45),
            inset 0 1px 0 rgba(255,255,255,0.06);
        margin-bottom: 28px;
    }

    .premium-hero h1 {
        font-size: 2.55rem;
        font-weight: 950;
        margin-bottom: 10px;
    }

    .premium-hero p {
        color: #d1d5db;
        font-size: 1.02rem;
        line-height: 1.7;
        max-width: 1000px;
    }

    /* -----------------------------
       PREMIUM CARDS
    ----------------------------- */
    .premium-card,
    .metric-card,
    .agent-card,
    .insight-card {
        background: rgba(15,23,42,0.88) !important;
        border: 1px solid rgba(34,197,94,0.24);
        border-radius: 18px;
        box-shadow:
            0 14px 36px rgba(0,0,0,0.32),
            inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .metric-card {
        padding: 20px;
        min-height: 118px;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.82rem;
        font-weight: 750;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.75rem;
        font-weight: 950;
        margin-top: 10px;
    }

    .metric-note {
        color: #86efac;
        font-size: 0.8rem;
        margin-top: 8px;
        font-weight: 700;
    }

    .insight-card {
        padding: 18px 20px;
        color: #e5e7eb;
        margin-bottom: 12px;
    }

    .insight-good { border-left: 4px solid #22c55e; }
    .insight-risk { border-left: 4px solid #f59e0b; }
    .insight-critical { border-left: 4px solid #ef4444; }

    .section-title {
        font-size: 1.25rem;
        font-weight: 900;
        color: #ffffff;
        margin: 1.7rem 0 0.9rem 0;
    }

    /* -----------------------------
       STREAMLIT BUILT-IN COMPONENTS
    ----------------------------- */
    div[data-testid="stMetric"] {
        background: rgba(15,23,42,0.88);
        border: 1px solid rgba(34,197,94,0.24);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 12px 32px rgba(0,0,0,0.28);
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
        border: 1px solid rgba(34,197,94,0.18);
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 14px !important;
        border: 1px solid rgba(34,197,94,0.55) !important;
        background: linear-gradient(135deg, #22c55e, #15803d) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 24px rgba(34,197,94,0.22);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #86efac !important;
        box-shadow: 0 0 22px rgba(34,197,94,0.38);
        transform: translateY(-1px);
    }

    input, textarea {
        border-radius: 12px !important;
        border: 1px solid rgba(34,197,94,0.35) !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(34,197,94,0.18);
    }

    /* -----------------------------
       TABS / EXPANDERS
    ----------------------------- */
    [data-testid="stExpander"] {
        background: rgba(15,23,42,0.82);
        border: 1px solid rgba(34,197,94,0.22);
        border-radius: 16px;
    }

    button[data-baseweb="tab"] {
        color: #e5e7eb !important;
        font-weight: 700;
    }

    /* -----------------------------
       HIDE STREAMLIT DEFAULTS
    ----------------------------- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }

    /* -----------------------------
       MOBILE RESPONSIVE
    ----------------------------- */
    @media (max-width: 768px) {
        .premium-hero {
            padding: 24px;
        }

        .premium-hero h1 {
            font-size: 2rem;
        }

        .metric-value {
            font-size: 1.45rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def metric_card(label, value, note=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def insight_card(message, level="good"):
    css_class = {
        "good": "insight-good",
        "risk": "insight-risk",
        "critical": "insight-critical",
    }.get(level, "insight-good")

    st.markdown(f"""
    <div class="insight-card {css_class}">
        {message}
    </div>
    """, unsafe_allow_html=True)


def premium_hero(title, subtitle):
    st.markdown(f"""
    <div class="premium-hero">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def section_title(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def style_plotly(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        title_font=dict(size=18, color="#ffffff"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5e7eb")
        ),
        margin=dict(l=20, r=20, t=55, b=25),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.15)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.15)")
    return fig
    
def setup_page(title, icon="🥬"):
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    inject_css()
