import streamlit as st
import time

# =========================================================
# GLOBAL CSS (ELITE UI)
# =========================================================
def inject_css():
    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at 18% 18%, rgba(34,197,94,0.18), transparent 30%),
            linear-gradient(135deg, #020403 0%, #050807 45%, #07130c 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1350px;
        padding-top: 2rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #06120d, #020403);
    }

    /* Typography */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 900 !important;
    }

    /* Cards */
    .metric-card {
        padding: 20px;
        border-radius: 20px;
        background: rgba(15,23,42,0.85);
        border: 1px solid rgba(34,197,94,0.25);
    }

    .metric-label {
        font-size: 0.8rem;
        color: #9ca3af;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 900;
        color: #ffffff;
    }

    .metric-note {
        color: #86efac;
        font-size: 0.8rem;
    }

    /* Buttons */
    .stButton button {
        border-radius: 14px;
        background: linear-gradient(135deg, #22c55e, #15803d);
        color: white;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)


# =========================================================
# PAGE SETUP
# =========================================================
def setup_page(title, icon="🥬"):
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    inject_css()
    init_copilot_state()


# =========================================================
# HERO
# =========================================================
def premium_hero(title, subtitle, badge="AI Operations Intelligence"):
    st.markdown(f"""
    <div style="
        position: relative;
        overflow: hidden;
        padding: 34px 38px;
        border-radius: 28px;
        background:
            linear-gradient(135deg, rgba(15,23,42,0.98), rgba(6,78,59,0.82)),
            radial-gradient(circle at top right, rgba(34,197,94,0.32), transparent 38%);
        border: 1px solid rgba(34,197,94,0.42);
        box-shadow: 0 24px 65px rgba(0,0,0,0.45);
        margin-bottom: 26px;
    ">
        <div style="
            display:inline-block;
            padding:7px 13px;
            border-radius:999px;
            background:rgba(34,197,94,0.16);
            color:#86efac;
            border:1px solid rgba(34,197,94,0.35);
            font-weight:850;
            font-size:0.78rem;
            margin-bottom:12px;
        ">
            {badge}
        </div>
        <h1 style="font-size:2.45rem;font-weight:950;margin-bottom:10px;color:#fff;">
            {title}
        </h1>
        <p style="color:#d1d5db;font-size:1.03rem;line-height:1.7;max-width:1050px;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# METRICS
# =========================================================
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
    <div style="
        padding:20px;
        min-height:155px;
        border-radius:20px;
        background:rgba(15,23,42,0.82);
        border:1px solid rgba(34,197,94,0.24);
        box-shadow:0 18px 45px rgba(0,0,0,0.32);
        color:#e5e7eb;
        margin-bottom:12px;
    ">
        <div style="
            color:#86efac;
            font-size:1rem;
            font-weight:900;
            margin-bottom:10px;
        ">
            {title}
        </div>
        <div>{body}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# INSIGHTS
# =========================================================
def insight_card(message, level="good"):
    colors = {
        "good": "#22c55e",
        "risk": "#f59e0b",
        "critical": "#ef4444"
    }
    color = colors.get(level, "#22c55e")

    st.markdown(f"""
    <div style="
        border-left:5px solid {color};
        padding:15px;
        border-radius:12px;
        background: rgba(15,23,42,0.8);
        margin-bottom:10px;
    ">
        {message}
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SECTION TITLE
# =========================================================
def section_title(title):
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)


# =========================================================
# PLOTLY DARK STYLE
# =========================================================
def style_plotly(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
    )
    return fig


# =========================================================
# STREAMING TEXT (CHATGPT EFFECT)
# =========================================================
def stream_text(text, speed=0.01):
    words = str(text).split(" ")
    for word in words:
        yield word + " "
        time.sleep(speed)


# =========================================================
# GLOBAL COPILOT STATE
# =========================================================
def init_copilot_state():
    if "global_copilot_open" not in st.session_state:
        st.session_state.global_copilot_open = False

    if "global_copilot_history" not in st.session_state:
        st.session_state.global_copilot_history = []

    if "copilot_context" not in st.session_state:
        st.session_state.copilot_context = ""


# =========================================================
# SET CONTEXT PER PAGE
# =========================================================
def set_copilot_context(text):
    st.session_state.copilot_context = text


# =========================================================
# GLOBAL COPILOT UI
# =========================================================
def render_global_copilot(generate_fn):
    st.markdown("---")
    st.markdown("## 🤖 AI Copilot")

    user_input = st.chat_input("Ask anything about this page...")

    if user_input:
        st.session_state.global_copilot_history.append(("user", user_input))

        full_prompt = f"""
        Context:
        {st.session_state.copilot_context}

        Question:
        {user_input}

        Give actionable business insights.
        """

        response = generate_fn(full_prompt)

        st.session_state.global_copilot_history.append(("ai", response))

    # Display chat
    for role, msg in st.session_state.global_copilot_history:
        with st.chat_message(role):
            if role == "ai":
                st.write_stream(stream_text(msg))
            else:
                st.write(msg)


# =========================================================
# VOICE INPUT (OPTIONAL)
# =========================================================
def voice_input():
    import speech_recognition as sr

    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except:
        st.error("Voice not recognized")
        return None
