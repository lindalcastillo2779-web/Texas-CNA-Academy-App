"""Home / welcome page."""

import streamlit as st

from db import get_or_create_user, get_user_by_email
from email_utils import send_welcome_email

ROLES = ["student", "cna", "don", "instructor", "facility"]


def show() -> None:
    st.title("🌸 Welcome to Texas CNA Academy")
    st.subheader("TULIP-Link Portal")

    st.markdown(
        """
        The **Texas CNA Academy (TULIP-Link)** portal is your one-stop destination for:

        | Feature | Who benefits |
        |---|---|
        | 📚 NATCEP exam practice quizzes | Students preparing for certification |
        | 📋 CEU hour tracking & certificates | Active CNAs, renewal candidates |
        | ✅ Renewal readiness dashboard | CNAs & DONs |
        | 🏥 Staffing compliance log | Facilities, DONs |

        Use the **sidebar** to navigate between sections.
        """
    )

    st.divider()

    # Session state
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""

    if st.session_state["user_id"]:
        st.success(f"✅ Signed in as **{st.session_state['user_name']}**")
        if st.button("Sign out"):
            st.session_state["user_id"] = None
            st.session_state["user_name"] = ""
            st.rerun()
        return

    tab_login, tab_register = st.tabs(["Sign In", "Register"])

    with tab_login:
        st.subheader("Sign In")
        email = st.text_input("Email address", key="login_email")
        if st.button("Sign In", key="sign_in_btn"):
            if not email:
                st.warning("Please enter your email.")
            else:
                user = get_user_by_email(email.strip().lower())
                if user:
                    st.session_state["user_id"] = user["id"]
                    st.session_state["user_name"] = user["name"]
                    st.success(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("No account found for that email. Please register first.")

    with tab_register:
        st.subheader("Create an Account")
        with st.form("register_form"):
            r_name  = st.text_input("Full name")
            r_email = st.text_input("Email address")
            r_role  = st.selectbox("Role", ROLES)
            submitted = st.form_submit_button("Register")

        if submitted:
            if not r_name or not r_email:
                st.warning("Name and email are required.")
            else:
                existing = get_user_by_email(r_email.strip().lower())
                if existing:
                    st.info("An account with that email already exists. Please sign in.")
                else:
                    uid = get_or_create_user(r_name.strip(), r_email.strip().lower(), r_role)
                    st.session_state["user_id"] = uid
                    st.session_state["user_name"] = r_name.strip()
                    send_welcome_email(r_name.strip(), r_email.strip().lower())
                    st.success(f"Account created! Welcome, {r_name}.")
                    st.rerun()
