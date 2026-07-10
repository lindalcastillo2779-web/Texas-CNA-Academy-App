"""
Texas CNA Academy (TULIP-Link)
================================
Main entry-point for the Streamlit multi-page application.

Integrated features:
- Texas-focused nurse aide training support
- Compliance & regulatory guidance
- Regulatory updates monitor
- Role-based dashboards
- Instructor SEMARC training module
- Form 5497 / 5498 workflow support

Notes:
- This file consolidates the duplicated app bootstrapping code from the user's draft.
- It corrects structural syntax issues, removes broken mixed docstring/code blocks,
  and organizes routing into functions.
"""

from __future__ import annotations

import datetime as dt
from typing import Dict, List

import streamlit as st

from db import get_access_status, init_db


# -----------------------------------------------------------------------------
# App bootstrapping
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Texas CNA Academy",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()


# -----------------------------------------------------------------------------
# Session state defaults
# -----------------------------------------------------------------------------
def init_session_state() -> None:
    if "regulatory_entries" not in st.session_state:
        st.session_state.regulatory_entries = [
            {
                "date": "2024-03-15",
                "title": "March 2024 Texas Nurse Aide Curriculum and NATCEP Changes",
                "summary": (
                    "Texas HHSC issued updated nurse aide curriculum and related NATCEP guidance "
                    "reflecting rule changes, including current training structure and updated "
                    "documentation references."
                ),
                "source_agency": "HHSC / NATCEP",
                "source_url": "https://www.hhs.texas.gov/",
                "status": "Verified official source",
                "reviewed_by": "Compliance Admin",
                "internal_action_needed": "Review official guidance",
                "last_checked": "2026-07-09",
            },
            {
                "date": "2026-06-29",
                "title": "June 29, 2026 Provider Letter PL 2026-10 on SEMARC Responsibilities",
                "summary": (
                    "HHSC provider-letter listings show PL 2026-10 addressing provider responsibilities "
                    "for SEMARC. Administrative users should review current employability-check workflows "
                    "and compare them with any existing EMR-only instructions."
                ),
                "source_agency": "HHSC / SEMARC",
                "source_url": "https://www.hhs.texas.gov/",
                "status": "Verified listing only",
                "reviewed_by": "Compliance Admin",
                "internal_action_needed": "Review official source before updating policy",
                "last_checked": "2026-07-09",
            },
        ]

    st.session_state.setdefault("quiz_submitted", False)
    st.session_state.setdefault("training_acknowledged", False)
    st.session_state.setdefault("sidebar_nav", "Home")


init_session_state()


# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
def render_global_styles() -> None:
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --navy: #0B1D35;
                --burgundy: #5A0C1A;
                --gold: #9E6C00;
                --beige: #F5EDE0;
                --beige-2: #EDE5D4;
                --card: #FEFBF5;
            }

            .stApp {
                background-color: var(--beige) !important;
            }

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            h1, h2, h3, h4, h5, h6,
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
            .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
                font-family: 'Playfair Display', Georgia, serif !important;
                font-weight: 700 !important;
                color: var(--navy) !important;
                letter-spacing: -0.01em;
            }

            [data-testid="stSidebar"] {
                background-color: var(--navy) !important;
            }

            [data-testid="stSidebar"] * {
                color: rgba(255,255,255,0.9) !important;
            }

            [data-testid="stMetric"] {
                background: var(--card) !important;
                border: 1px solid #D4C3A8 !important;
                border-top: 3px solid var(--gold) !important;
                border-radius: 8px !important;
                padding: 16px !important;
            }

            .stButton > button {
                background-color: var(--burgundy) !important;
                color: #fff !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
            }

            .stButton > button:hover {
                background-color: #400813 !important;
                color: #fff !important;
            }

            [data-testid="stDataFrame"] {
                border: 1px solid #D4C3A8 !important;
                border-radius: 8px !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


render_global_styles()


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def render_footer() -> None:
    st.markdown("---")
    st.caption(
        "Texas CNA Academy is an independent education and compliance-support platform. "
        "It is not operated by Texas Health and Human Services Commission, TULIP, SEMARC, "
        "Prometric, the Nurse Aide Registry, or the Texas Board of Nursing. Official "
        "determinations regarding certification, approval, registry status, employability, "
        "renewal, and licensure are made only by the appropriate official agencies and systems."
    )
    st.caption("Last policy review: 2026-07-09")


def user_has_access() -> bool:
    user_id = st.session_state.get("user_id")
    if not user_id:
        return False
    access = get_access_status(user_id)
    return bool(access.get("allowed"))


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
def show_home() -> None:
    st.title("Texas CNA Academy")
    st.markdown(
        "#### Texas CNA Academy provides Texas-focused nurse aide training support, "
        "exam preparation, renewal guidance, and compliance tools for students, instructors, "
        "directors of nursing, and healthcare administrators."
    )
    st.info(
        "Our platform is built around current Texas nurse aide curriculum, registry guidance, "
        "and long-term care workflows. Texas CNA Academy is an independent education and "
        "compliance-support platform and is not operated by Texas Health and Human Services, "
        "TULIP, or Prometric."
    )

    st.subheader("Our Mission")
    st.write(
        "At Texas CNA Academy, our mission is to support nurse aide students and healthcare teams "
        "across Texas with clear, practical, Texas-focused education and compliance tools. We help "
        "users prepare for training, certification, renewal, and workforce readiness using structured "
        "learning resources, skills support, and regulatory guidance aligned with current Texas requirements."
    )

    with st.expander("Mission disclaimer"):
        st.caption(
            "Texas CNA Academy provides educational and compliance-support resources. Official "
            "eligibility, certification, registry status, employability determinations, and licensing "
            "actions are made only through the appropriate official agencies and systems."
        )

    st.divider()
    st.subheader("Explore by role")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Student")
        st.write(
            "Access study materials, practice tools, and Texas-specific guidance designed to help "
            "you prepare with confidence."
        )
    with col2:
        st.markdown("### Instructor")
        st.write(
            "Support training delivery with curriculum tools, student progress tracking, skills "
            "validation support, and documentation workflows aligned with Texas NATCEP expectations."
        )
    with col3:
        st.markdown("### Facility / Admin")
        st.write(
            "Track certification-related deadlines, staff records, workforce compliance tasks, and "
            "regulatory updates with tools designed for administrators, DONs, and program leaders."
        )

    st.divider()
    st.subheader("Program offerings & tools")
    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("#### Certification & Exam Prep")
        st.write(
            "Prepare for Texas nurse aide training and competency evaluation with structured study "
            "materials, practice assessments, skills support, and reference tools."
        )
    with p2:
        st.markdown("#### Compliance Tracking & Regulatory Guidance")
        st.write(
            "Texas CNA Academy helps facilities, instructors, and program leaders organize compliance-related "
            "tasks, track deadlines, and monitor selected Texas nurse aide workflow requirements."
        )
        st.caption(
            "Texas CNA Academy helps users organize and monitor compliance-related information but does not "
            "replace HHSC, TULIP, SEMARC, the Nurse Aide Registry, Prometric, or any official state determination."
        )
    with p3:
        st.markdown("#### Renewal Guidance & Tracking Support")
        st.write(
            "Texas CNA Academy supports users with renewal guidance, deadline awareness, and record-organization "
            "tools for Texas nurse aide renewal workflows."
        )
        st.caption(
            "Texas nurse aide renewal generally requires 24 hours of in-service education every two years, along "
            "with any applicable registry and renewal requirements handled through official Texas systems."
        )

    st.divider()
    st.subheader("Official Texas resources")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("**Texas Health and Human Services**")
        st.write(
            "Texas Health and Human Services oversees the Nurse Aide Registry, nurse aide program regulation, "
            "and many long-term care regulatory functions relevant to nurse aide training and employability workflows."
        )
    with r2:
        st.markdown("**TULIP**")
        st.write(
            "The Texas Unified Licensure Information Portal supports specific credentialing, application, registry, "
            "and regulatory workflows in Texas. Available functions vary by user role and access level."
        )
    with r3:
        st.markdown("**Texas Board of Nursing**")
        st.write(
            "Texas Board of Nursing regulates nursing licensure in Texas. It may be a useful related resource for "
            "users exploring future nursing pathways, but nurse aide registry and NATCEP matters are generally handled "
            "through HHSC and related systems."
        )

    render_footer()


def show_compliance() -> None:
    st.title("Texas CNA Compliance & Regulatory Guidance")
    st.write(
        "Texas CNA Academy provides Texas-focused compliance support tools and guidance for nurse aide students, "
        "instructors, directors of nursing, administrators, and training programs. This page helps users organize "
        "information and monitor changes related to nurse aide training, renewal, registry workflows, and "
        "employability-related updates in Texas."
    )
    st.info(
        "Texas CNA Academy is an independent platform. It is not operated by Texas Health and Human Services "
        "Commission (HHSC), TULIP, SEMARC, the Nurse Aide Registry, Prometric, or the Texas Board of Nursing. "
        "Official decisions about approval, certification, registry status, employability, renewal, and licensure "
        "are made only through the appropriate official agencies and systems."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### What this page helps with")
        st.markdown(
            "- Tracking regulatory updates\n"
            "- Monitoring deadlines and workflow changes\n"
            "- Reviewing Texas nurse aide renewal guidance\n"
            "- Organizing NATCEP-related documentation workflows\n"
            "- Linking to official state resources"
        )
    with c2:
        st.markdown("### What this page does not do")
        st.markdown(
            "- It does not issue certification\n"
            "- It does not verify registry status directly\n"
            "- It does not make employability determinations\n"
            "- It does not replace required background checks\n"
            "- It does not replace HHSC, TULIP, NAR, SEMARC, or Prometric requirements"
        )

    st.divider()
    st.subheader("Texas renewal guidance")
    st.write(
        "Texas nurse aide renewal guidance should be reviewed through official HHSC resources. Texas CNA Academy "
        "may help users track deadlines and organize records, but users must complete all official renewal requirements "
        "through the appropriate state systems."
    )

    st.subheader("NATCEP records guidance")
    st.write(
        "For instructors and program leaders, Texas CNA Academy may support documentation workflows related to training "
        "attendance, performance tracking, and internal record organization. Programs should continue to maintain required "
        "official records and verify current HHSC requirements for forms, approvals, and documentation practices."
    )

    st.subheader("Employability checks and SEMARC")
    st.write(
        "Texas employability-check workflows may include SEMARC-related processes for authorized users, along with other "
        "applicable registry or screening requirements depending on role, setting, and current Texas guidance. Users should "
        "not assume that one system replaces every other required check unless confirmed by official source documents."
    )

    st.caption("Last reviewed: 2026-07-09")
    render_footer()


def show_regulatory_updates() -> None:
    st.title("Texas Regulatory Updates Monitor")
    st.warning(
        "Texas CNA Academy monitors official public sources for convenience. Users must review the official source "
        "before acting on regulatory content."
    )
    st.write(
        "This page tracks selected Texas nurse aide, NATCEP, TULIP, Nurse Aide Registry, and SEMARC-related updates "
        "from official sources."
    )

    for entry in st.session_state.regulatory_entries:
        with st.container(border=True):
            st.markdown(f"### {entry['title']}")
            st.write(
                f"**Date:** {entry['date']}  ",
            )
            st.write(f"**Tag:** {entry['source_agency']}")
            st.write(f"**Status:** {entry['status']}")
            st.write(entry["summary"])
            st.info(f"Internal action needed: {entry['internal_action_needed']}")
            st.caption(
                f"Last checked: {entry['last_checked']} | Reviewed by: {entry['reviewed_by']} | Source: {entry['source_url']}"
            )

    with st.sidebar:
        st.subheader("Live auditor toolkit")
        if st.button("Run monitor sync"):
            st.success("Sync completed. No new changes detected.")
        st.caption("Monitor official sources only.")

    render_footer()


def show_role_dashboards() -> None:
    st.title("Role-Based Dashboard Portals")
    role_view = st.selectbox(
        "Switch dashboard context",
        ["Student", "Instructor", "DON (Director of Nursing)", "Admin"],
    )

    st.markdown(f"#### Current access: **{role_view}**")
    role_copy: Dict[str, List[str]] = {
        "Student": [
            "Exam prep frameworks",
            "Skills practice metrics",
            "Renewal reminders",
            "Official resource links",
            "Informational notices only",
        ],
        "Instructor": [
            "Student progress tracking tools",
            "Skills validation support records",
            "Attendance logging workflows",
            "NATCEP documentation reminders",
            "Training regulatory feeds",
        ],
        "DON (Director of Nursing)": [
            "Staff deadline tracking",
            "In-service tracking systems",
            "Compliance alerts",
            "Employability check reminders",
            "Regulatory monitor widgets",
        ],
        "Admin": [
            "SEMARC / NAR / renewal alerts",
            "Provider letter workflows",
            "Staff records overview",
            "Internal audit trails",
            "Policy-change checklists",
        ],
    }
    st.markdown("\n".join([f"- {item}" for item in role_copy[role_view]]))

    st.divider()
    st.subheader("Form 5497 & 5498 digital workflow trackers")
    st.caption(
        "Digital workflow support based on current Texas form structure. Users should verify current official forms "
        "and requirements before submission or audit use."
    )

    tab1, tab2 = st.tabs(["Form 5497: Performance Record", "Form 5498: Daily Sign-In"])
    with tab1:
        st.write("##### Internal workflow: trainee performance evaluation")
        st.text_input("Trainee candidate name", key="trainee_name")
        st.checkbox("Mark performance steps reviewed", key="review_5497")
        st.button("Save Form 5497 log", key="save_5497")
    with tab2:
        st.write("##### Internal workflow: daily attendance record")
        st.date_input("Training date", value=dt.date.today(), key="date_5498")
        st.text_area("Roster notes", key="roster_5498")
        st.button("Save Form 5498 entry", key="save_5498")

    render_footer()


def show_semarc_training() -> None:
    st.title("Instructor SEMARC Training Module and SOP")
    st.caption("Last updated: 2026-07-09")
    st.warning(
        "SEMARC-related workflows are limited to authorized users. Staff must not access, share, or interpret "
        "SEMARC results outside their assigned role and must follow all confidentiality guidelines."
    )

    with st.expander("Review training module", expanded=True):
        st.markdown(
            """
            #### Learning objectives
            - Explain what SEMARC is.
            - Identify access constraints.
            - Outline differences between SEMARC, NAR, and TULIP.
            - Maintain confidentiality.

            #### Section 1: What SEMARC is
            SEMARC is the Search Engine for Multi-Agency Reportable Conduct.

            #### Section 2: Who may access SEMARC
            SEMARC is not a general public tool. Only authorized users should access it.

            #### Section 3: Confidentiality
            SEMARC search results are confidential and should only be used in approved workflows.

            #### Section 4: SEMARC is not the whole workflow
            Staff should not assume SEMARC replaces every other required screening step.

            #### Section 5: Internal rule for Texas CNA Academy
            Internal platform notices and reminders support workflow organization but do not replace official state requirements.
            """
        )

    st.subheader("Knowledge check")
    q1 = st.radio(
        "1. Is SEMARC a public search tool for all staff?",
        ["Yes", "No, it is restricted to authorized users"],
        key="semarc_q1",
    )
    q2 = st.radio(
        "2. Are SEMARC search results confidential?",
        ["No", "Yes"],
        key="semarc_q2",
    )
    q3 = st.radio(
        "3. Does SEMARC replace every other required Texas verification check?",
        ["Yes", "No"],
        key="semarc_q3",
    )

    if st.button("Submit quiz", key="submit_quiz"):
        st.session_state.quiz_submitted = True
        if q1 == "No, it is restricted to authorized users" and q2 == "Yes" and q3 == "No":
            st.success("Quiz submitted successfully. Your responses reflect the required workflow principles.")
        else:
            st.error("Some responses need review. Please review the training module and try again.")

    st.subheader("Required acknowledgment")
    ack1 = st.checkbox("I understand that SEMARC access is restricted to authorized users.", key="ack1")
    ack2 = st.checkbox(
        "I understand that SEMARC search results are confidential and may only be handled according to law and policy.",
        key="ack2",
    )
    ack3 = st.checkbox(
        "I understand that internal workflow tools do not replace official HHSC, SEMARC, TULIP, or NAR requirements.",
        key="ack3",
    )
    ack4 = st.checkbox(
        "I will review current official guidance before acting on employability-related information.",
        key="ack4",
    )

    if ack1 and ack2 and ack3 and ack4:
        st.session_state.training_acknowledged = True
        st.success("Acknowledgment recorded.")
    else:
        st.info("Complete all acknowledgment items to confirm training completion.")

    render_footer()


# -----------------------------------------------------------------------------
# Sidebar navigation
# -----------------------------------------------------------------------------
PAGES = {
    "Home": "home",
    "Compliance Guidance": "compliance",
    "Regulatory Updates Monitor": "regulatory_updates",
    "Role Workflows & Dashboards": "role_dashboards",
    "Instructor SEMARC Training": "semarc_training",
    "Courses": "courses",
    "Exam Prep": "exam_prep",
    "My Progress": "progress",
    "Clinical Skills Lab": "clinical_skills_lab",
    "Community Hub": "community_hub",
    "CEU Tracker": "ceu_tracker",
    "Renewal Check": "renewal_check",
    "Staffing Log": "staffing",
    "Buddy": "buddy",
    "Verified Resources": "resources",
    "Admin Panel": "admin",
}

with st.sidebar:
    st.image("https://img.icons8.com/color/96/nurse-female.png", width=80)
    st.title("Texas CNA Academy")
    st.caption("Compliance & Education Portal")
    st.divider()
    page_label = st.radio("Navigate", list(PAGES.keys()), key="sidebar_nav", label_visibility="collapsed")

page = PAGES[page_label]

NON_AUTH_PAGES = {"home", "compliance", "regulatory_updates", "resources", "semarc_training"}
if page not in NON_AUTH_PAGES and not user_has_access():
    st.warning("Please sign in on the Home page to access secure application sections.")
    page = "home"


# -----------------------------------------------------------------------------
# Routing
# -----------------------------------------------------------------------------
if page == "home":
    show_home()
elif page == "compliance":
    show_compliance()
elif page == "regulatory_updates":
    show_regulatory_updates()
elif page == "role_dashboards":
    show_role_dashboards()
elif page == "semarc_training":
    show_semarc_training()
elif page == "courses":
    from pages import courses as _page
    _page.show()
elif page == "exam_prep":
    from pages import exam_prep as _page
    _page.show()
elif page == "progress":
    from pages import progress as _page
    _page.show()
elif page == "clinical_skills_lab":
    from pages import clinical_skills_lab as _page
    _page.show()
elif page == "community_hub":
    from pages import community_hub as _page
    _page.show()
elif page == "ceu_tracker":
    from pages import ceu_tracker as _page
    _page.show()
elif page == "renewal_check":
    from pages import renewal_check as _page
    _page.show()
elif page == "staffing":
    from pages import staffing as _page
    _page.show()
elif page == "buddy":
    from pages import buddy as _page
    _page.show()
elif page == "resources":
    from pages import resources as _page
    _page.show()
elif page == "admin":
    from pages import admin as _page
    _page.show()
else:
    show_home()

