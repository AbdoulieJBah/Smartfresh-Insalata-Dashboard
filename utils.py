import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(34,197,94,0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(59,130,246,0.10), transparent 26%),
            linear-gradient(135deg, #020403 0%, #050807 45%, #07130c 100%) !important;
        color: #f8fafc !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1350px;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #06120d 0%, #081b12 55%, #020403 100%) !important;
        border-right: 1px solid rgba(34,197,94,0.30);
    }

    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    section[data-testid="stSidebarNav"] {
        display: none;
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
        letter-spacing: -0.02em;
    }

    p, span, label, div {
        font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    .premium-hero {
        position: relative;
        overflow: hidden;
        padding: 36px 40px;
        border-radius: 30px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.98), rgba(6,78,59,0.78)),
            radial-gradient(circle at top right, rgba(34,197,94,0.32), transparent 38%);
        border: 1px solid rgba(34,197,94,0.45);
        box-shadow:
            0 26px 70px rgba(0,0,0,0.48),
            inset 0 1px 0 rgba(255,255,255,0.08);
        margin-bottom: 28px;
        animation: fadeInUp 0.65s ease both;
    }

    .premium-hero::before {
        content: "";
        position: absolute;
        inset: -2px;
        background: linear-gradient(90deg, transparent, rgba(34,197,94,0.18), transparent);
        transform: translateX(-100%);
        animation: shimmer 4s infinite;
    }

    .premium-hero h1 {
        position: relative;
        font-size: 2.65rem;
        font-weight: 950;
        margin-bottom: 10px;
        z-index: 2;
    }

    .premium-hero p {
        position: relative;
        color: #d1d5db;
        font-size: 1.03rem;
        line-height: 1.75;
        max-width: 1050px;
        z-index: 2;
    }

    .hero-badge {
        position: relative;
        z-index: 2;
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(34,197,94,0.16);
        color: #86efac;
        border: 1px solid rgba(34,197,94,0.35);
        font-weight: 800;
        font-size: 0.78rem;
        margin-bottom: 12px;
    }

    .glass-card,
    .metric-card,
    .agent-card,
    .insight-card {
        background: rgba(15,23,42,0.78) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(34,197,94,0.24);
        border-radius: 20px;
        box-shadow:
            0 18px 45px rgba(0,0,0,0.35),
            inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.25s ease;
        animation: fadeInUp 0.55s ease both;
    }

    .glass-card:hover,
    .metric-card:hover,
    .agent-card:hover,
    .insight-card:hover {
        transform: translateY(-3px);
        border-color: rgba(34,197,94,0.48);
        box-shadow:
            0 24px 60px rgba(0,0,0,0.45),
            0 0 25px rgba(34,197,94,0.10);
    }

    .metric-card {
        padding: 21px;
        min-height: 120px;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.78rem;
        font-weight: 950;
        margin-top: 10px;
        word-break: break-word;
    }

    .metric-note {
        color: #86efac;
        font-size: 0.8rem;
        margin-top: 8px;
        font-weight: 750;
    }

    .agent-card {
        padding: 20px;
        color: #e5e7eb;
        min-height: 165px;
    }

    .agent-title {
        color: #86efac;
        font-size: 1rem;
        font-weight: 900;
        margin-bottom: 10px;
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
        font-size: 1.26rem;
        font-weight: 950;
        color: #ffffff;
        margin: 1.8rem 0 0.95rem 0;
        letter-spacing: -0.02em;
    }

    .section-subtitle {
        color: #9ca3af;
        font-size: 0.92rem;
        margin-top: -0.5rem;
        margin-bottom: 1rem;
    }

    .status-pill {
        display: inline-block;
        padding: 6px 11px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 800;
        border: 1px solid rgba(255,255,255,0.12);
    }

    .pill-green {
        background: rgba(34,197,94,0.15);
        color: #86efac;
        border-color: rgba(34,197,94,0.35);
    }

    .pill-yellow {
        background: rgba(245,158,11,0.15);
        color: #fbbf24;
        border-color: rgba(245,158,11,0.35);
    }

    .pill-red {
        background: rgba(239,68,68,0.15);
        color: #fca5a5;
        border-color: rgba(239,68,68,0.35);
    }

    div[data-testid="stMetric"] {
        background: rgba(15,23,42,0.78);
        border: 1px solid rgba(34,197,94,0.24);
        border-radius: 20px;
        padding: 18px;
        box-shadow: 0 14px 36px rgba(0,0,0,0.30);
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
        font-weight: 850 !important;
        box-shadow: 0 12px 26px rgba(34,197,94,0.24);
        transition: all 0.22s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #86efac !important;
        box-shadow: 0 0 24px rgba(34,197,94,0.40);
        transform: translateY(-1px);
    }

    input, textarea {
        border-radius: 14px !important;
        border: 1px solid rgba(34,197,94,0.35) !important;
        background: rgba(15,23,42,0.70) !important;
        color: #f8fafc !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(34,197,94,0.20);
        box-shadow: 0 14px 36px rgba(0,0,0,0.28);
    }

    [data-testid="stExpander"] {
        background: rgba(15,23,42,0.82);
        border: 1px solid rgba(34,197,94,0.22);
        border-radius: 16px;
    }

    button[data-baseweb="tab"] {
        color: #e5e7eb !important;
        font-weight: 750;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        55% { transform: translateX(100%); }
        100% { transform: translateX(100%); }
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }

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


def setup_page(title, icon="🥬"):
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    inject_css()


def premium_hero(title, subtitle, badge="AI Operations Intelligence"):
    st.markdown(f"""
    <div class="premium-hero">
        <div class="hero-badge">{badge}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label, value, note=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def agent_card(title, body):
    st.markdown(f"""
    <div class="agent-card">
        <div class="agent-title">{title}</div>
        <div>{body}</div>
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


def section_title(title, subtitle=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

    if subtitle:
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def status_pill(text, level="green"):
    level_class = {
        "green": "pill-green",
        "yellow": "pill-yellow",
        "red": "pill-red",
    }.get(level, "pill-green")

    st.markdown(f"""
    <span class="status-pill {level_class}">{text}</span>
    """, unsafe_allow_html=True)


def glass_card(content):
    st.markdown(f"""
    <div class="glass-card" style="padding: 20px; margin-bottom: 12px;">
        {content}
    </div>
    """, unsafe_allow_html=True)


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
