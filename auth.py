"""Admin authentication helpers for Texas CNA Academy."""

import os
import streamlit as st


def _admin_secret() -> str:
    """Return the admin secret from env var or secrets.toml."""
    env_secret = os.environ.get("ADMIN_SECRET", "")
    if env_secret:
        return env_secret
    try:
        return st.secrets.get("admin", {}).get("secret", "")
    except Exception:
        return ""


def check_admin_password(password: str) -> bool:
    """Return True when *password* matches the configured ADMIN_SECRET."""
    secret = _admin_secret()
    if not secret:
        return False
    return password == secret


def require_admin() -> bool:
    """
    Render an admin login form in the sidebar.
    Returns True when the user is authenticated as admin.
    Stores the authenticated state in st.session_state.
    """
    if st.session_state.get("admin_authenticated"):
        return True

    with st.sidebar:
        st.subheader("🔐 Admin Login")
        pwd = st.text_input("Admin password", type="password", key="admin_pwd_input")
        if st.button("Login", key="admin_login_btn"):
            if check_admin_password(pwd):
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False
