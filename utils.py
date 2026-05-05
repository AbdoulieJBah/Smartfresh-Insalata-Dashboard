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
def premium_hero(title, subtitle):
    st.markdown(f"""
    <div style="
        padding:30px;
        border-radius:25px;
        background: linear-gradient(135deg,#0f172a,#065f46);
        margin-bottom:20px;
    ">
        <h1>{title}</h1>
        <p>{subtitle}</p>
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
