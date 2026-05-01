import streamlit as st


# -----------------------------
# AUTH CHECK
# -----------------------------
def require_auth():
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.warning("🔒 Please login first to access this page.")
        st.stop()


# -----------------------------
# ROLE CHECK
# -----------------------------
def require_role(allowed_roles):
    require_auth()

    user = st.session_state.get("user", {})
    role = user.get("role")

    if role not in allowed_roles:
        st.error("⛔ Access Denied")
        st.caption(f"Required roles: {', '.join(allowed_roles)}")
        st.stop()


# -----------------------------
# GET CURRENT USER
# -----------------------------
def get_current_user():
    return st.session_state.get("user", {})


# -----------------------------
# GET CURRENT ROLE
# -----------------------------
def get_current_role():
    user = get_current_user()
    return user.get("role", None)


# -----------------------------
# ROLE HELPERS (FOR CLEAN CODE)
# -----------------------------
def is_admin():
    return get_current_role() == "Admin"


def is_manager():
    return get_current_role() == "Manager"


def is_operations():
    return get_current_role() == "Operations"


def is_quality():
    return get_current_role() == "Quality"


def is_logistics():
    return get_current_role() == "Logistics"
