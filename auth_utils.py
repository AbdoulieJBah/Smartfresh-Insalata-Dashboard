import streamlit as st

def require_auth():
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.warning("🔒 Please login first")
        st.stop()


def require_role(allowed_roles):
    require_auth()

    user = st.session_state.get("user", {})
    role = user.get("role", None)

    if role not in allowed_roles:
        st.error("⛔ You do not have permission to access this page")
        st.stop()
