"""Home / welcome page."""

import os

import streamlit as st

from db import get_access_status, get_or_create_user, get_user_by_email
from email_utils import send_welcome_email
from utils.media import render_page_media

ROLES = ["student", "cna", "don", "instructor", "facility"]
SUBSCRIPTION_URL = os.getenv("SUBSCRIPTION_URL", "https://texascnaacademyapp.com/signup.html")
DESTINATIONS = [
    ("🎓 Courses", "courses"),
    ("📚 Exam Prep", "exam_prep"),
    ("📊 My Progress", "progress"),
    ("🧪 Clinical Skills Lab", "clinical_skills_lab"),
    ("📋 CEU Tracker", "ceu_tracker"),
    ("✅ Renewal Check", "renewal_check"),
    ("🏥 Staffing Log", "staffing"),
    ("🤖 Buddy", "buddy"),
    ("📎 Verified Resources", "resources"),
]


def show() -> None:
    st.title("🌸 Welcome to Texas CNA Academy")
    st.subheader("TULIP-Link Portal")
    render_page_media("home")

    st.markdown(
        """
        The **Texas CNA Academy (TULIP-Link)** portal is your one-stop destination for:

        | Feature | Who benefits |
        |---|---|
        | 🎓 NATCEP course roadmap & module library | Students building step-by-step readiness |
        | 📚 NATCEP exam practice quizzes | Students preparing for certification |
        | 📋 CEU hour tracking & certificates | Active CNAs, renewal candidates |
        | ✅ Renewal readiness dashboard | CNAs & DONs |
        | 🏥 Staffing compliance log | Facilities, DONs |

        You can use the quick links below or the **sidebar** to navigate between sections.
        """
    )
    st.subheader("Quick Links")
    cols = st.columns(2)
    for idx, (label, target) in enumerate(DESTINATIONS):
        with cols[idx % 2]:
            if st.button(label, key=f"home_nav_{target}", use_container_width=True):
                st.session_state["nav_target"] = target
                st.rerun()

    st.divider()

    # Session state
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""

    if st.session_state["user_id"]:
        st.success(f"✅ Signed in as **{st.session_state['user_name']}**")
        access = get_access_status(st.session_state["user_id"])
        if access["subscribed"]:
            st.info("✅ Subscription is active.")
        elif access["trial_active"]:
            st.info(
                f"🎁 Free trial active: {access['days_left']} day(s) left "
                f"(ends {access['trial_ends_on']})."
            )
        else:
            st.error("Your 30-day free trial has ended.")
            st.link_button("Start Subscription", SUBSCRIPTION_URL, use_container_width=True)

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
                    st.info("🎁 You now have a 30-day free trial before subscription is required.")
                    st.rerun()
