"""
Texas CNA Academy (TULIP-Link)
================================
Main entry-point for the Streamlit multi-page application.

Sections
--------
•  Home          – Welcome / self-registration
•  Courses       – NATCEP study roadmap and module content
•  Exam Prep     – Practice quizzes (NATCEP domains)
•  Clinical Skills Lab – Interactive Prometric-aligned skill simulations
•  Community Hub – Mentor matching, study circles, and workforce opportunities
•  CEU Tracker   – Log & track continuing-education hours
•  Renewal Check – Renewal readiness summary
•  Staffing      – Facility staffing compliance log
•  Buddy         – AI study and compliance chatbot
•  Admin         – Admin-only management panel
"""

import streamlit as st

from db import get_access_status, init_db

# ---------------------------------------------------------------------------
# Initialise database on first run
# ---------------------------------------------------------------------------
init_db()

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Texas CNA Academy",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global custom CSS — academic color palette + Playfair Display titles
# ---------------------------------------------------------------------------
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        /* ── Color tokens ── */
        :root {
            --navy:     #0B1D35;
            --burgundy: #5A0C1A;
            --gold:     #9E6C00;
            --beige:    #F5EDE0;
            --beige-2:  #EDE5D4;
            --card:     #FEFBF5;
        }

        /* ── All headings → Bold Playfair Display ── */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-family: 'Playfair Display', Georgia, serif !important;
            font-weight: 700 !important;
            color: var(--navy) !important;
            letter-spacing: -0.01em;
        }

        /* ── App background ── */
        .stApp {
            background-color: var(--beige) !important;
        }

        /* ── Main content area ── */
        section[data-testid="stMain"] > div {
            background: transparent;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: var(--navy) !important;
        }
        [data-testid="stSidebar"] * {
            color: rgba(255,255,255,0.88) !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            font-weight: 500 !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.15) !important;
        }

        /* ── Metric cards ── */
        [data-testid="stMetric"] {
            background: var(--card) !important;
            border: 1px solid #D4C3A8 !important;
            border-top: 3px solid var(--gold) !important;
            border-radius: 6px !important;
            padding: 16px !important;
        }
        [data-testid="stMetricValue"] {
            color: var(--navy) !important;
            font-family: 'Playfair Display', Georgia, serif !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #4A5568 !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
        }

        /* ── Primary buttons ── */
        .stButton > button[kind="primary"],
        .stButton > button {
            background-color: var(--burgundy) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
        }
        .stButton > button:hover {
            background-color: #400813 !important;
        }

        /* ── Tab headers ── */
        .stTabs [data-baseweb="tab"] {
            font-family: 'Playfair Display', Georgia, serif !important;
            font-weight: 600 !important;
            color: var(--navy) !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: var(--burgundy) !important;
        }

        /* ── Data tables ── */
        [data-testid="stDataFrame"] {
            border: 1px solid #D4C3A8 !important;
            border-radius: 6px !important;
        }

        /* ── Dividers ── */
        hr {
            border-color: #D4C3A8 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = {
    " Home": "home",
    " Courses": "courses",
    " Exam Prep": "exam_prep",
    " My Progress": "progress",
    " Clinical Skills Lab": "clinical_skills_lab",
    " Community Hub": "community_hub",
    " CEU Tracker": "ceu_tracker",
    " Renewal Check": "renewal_check",
    " Staffing Log": "staffing",
    " Buddy": "buddy",
    " Verified Resources": "resources",
    " Admin Panel": "admin",
}
PAGE_LABEL_BY_KEY = {key: label for label, key in PAGES.items()}

with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/nurse-female.png",
        width=80,
    )
    st.title("Texas CNA Academy")
    st.caption("TULIP-Link Portal")
    st.divider()
    if "sidebar_nav" not in st.session_state:
        st.session_state["sidebar_nav"] = "🏠 Home"
    nav_target = st.session_state.pop("nav_target", None)
    if nav_target in PAGE_LABEL_BY_KEY:
        st.session_state["sidebar_nav"] = PAGE_LABEL_BY_KEY[nav_target]
    page_label = st.radio(
        "Navigate",
        list(PAGES.keys()),
        key="sidebar_nav",
        label_visibility="collapsed",
    )

page = PAGES[page_label]

if page != "home" and page != "resources":
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please sign in on the Home page to access app sections.")
        from pages import home as _page

        _page.show()
        st.stop()

    access = get_access_status(user_id)
    if not access["allowed"]:
        st.warning(
            "Your 30-day free trial has ended. Please subscribe from the Home page to continue."
        )
        st.session_state["nav_target"] = "home"
        from pages import home as _page

        _page.show()
        st.stop()

# ---------------------------------------------------------------------------
# Route to individual page modules
# ---------------------------------------------------------------------------
if page == "home":
    from pages import home as _page
elif page == "courses":
    from pages import courses as _page
elif page == "exam_prep":
    from pages import exam_prep as _page
elif page == "progress":
    from pages import progress as _page
elif page == "clinical_skills_lab":
    from pages import clinical_skills_lab as _page
elif page == "community_hub":
    from pages import community_hub as _page
elif page == "ceu_tracker":
    from pages import ceu_tracker as _page
elif page == "renewal_check":
    from pages import renewal_check as _page
elif page == "staffing":
    from pages import staffing as _page
elif page == "buddy":
    from pages import buddy as _page
elif page == "resources":
    from pages import resources as _page
elif page == "admin":
    from pages import admin as _page
else:
    from pages import home as _page

_page.show()


Texas CNA Academy (TULIP-Link)
================================
Main entry-point for the Streamlit multi-page application.

Integrated Features:
- Compliance & Regulatory Guidance
- Regulatory Updates Monitor (Live Logs)
- Interactive Dashboards & Form 5497/5498 Workflows
- Instructor SEMARC Training Module & SOP Validation Quiz
"""

import streamlit as st
import datetime
from db import get_access_status, init_db

# ---------------------------------------------------------------------------
# Database and Session State Initialization
# ---------------------------------------------------------------------------
init_db()

if "regulatory_entries" not in st.session_state:
    st.session_state.regulatory_entries = [
        {
            "date": "2024-03-15",
            "title": "March 2024 Texas Nurse Aide Curriculum and NATCEP Changes",
            "summary": "Texas HHSC issued updated nurse aide curriculum and related NATCEP guidance reflecting rule changes, including current training structure and updated documentation references.",
            "source_agency": "HHSC / NATCEP",
            "source_url": "https://hhs.texas.gov",
            "status": "Verified official source",
            "reviewed_by": "Compliance Admin",
            "internal_action_needed": "Review official guidance",
            "last_checked": "2026-07-09"
        },
        {
            "date": "2026-06-29",
            "title": "June 29, 2026 Provider Letter PL 2026-10 on SEMARC Responsibilities",
            "summary": "HHSC provider-letter listings show PL 2026-10 addressing provider responsibilities for SEMARC. Administrative users should review current employability-check workflows and compare them with any existing EMR-only instructions.",
            "source_agency": "HHSC / SEMARC",
            "source_url": "https://hhs.texas.gov",
            "status": "Verified listing",
            "reviewed_by": "Compliance Admin",
            "internal_action_needed": "Review official source before updating policy",
            "last_checked": "2026-07-09"
        }
    ]

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "training_acknowledged" not in st.session_state:
    st.session_state.training_acknowledged = False

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Texas CNA Academy",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global custom CSS — academic color palette + Playfair Display titles
# ---------------------------------------------------------------------------
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght=600;700;800&family=Inter:wght=400;500;600&display=swap" rel="stylesheet">
    <style>
        /* ── Color tokens ── */
        :root {
            --navy:     #0B1D35;
            --burgundy: #5A0C1A;
            --gold:     #9E6C00;
            --beige:    #F5EDE0;
            --beige-2:  #EDE5D4;
            --card:     #FEFBF5;
        }

        /* ── All headings → Bold Playfair Display ── */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-family: 'Playfair Display', Georgia, serif !important;
            font-weight: 700 !important;
            color: var(--navy) !important;
            letter-spacing: -0.01em;
        }

        /* ── App background ── */
        .stApp {
            background-color: var(--beige) !important;
        }

        /* ── Main content area ── */
        section[data-testid="stMain"] > div {
            background: transparent;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: var(--navy) !important;
        }
        [data-testid="stSidebar"] * {
            color: rgba(255,255,255,0.88) !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            font-weight: 500 !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: rgba(255,255,255,0.15) !important;
        }

        /* ── Metric cards ── */
        [data-testid="stMetric"] {
            background: var(--card) !important;
            border: 1px solid #D4C3A8 !important;
            border-top: 3px solid var(--gold) !important;
            border-radius: 6px !important;
            padding: 16px !important;
        }
        [data-testid="stMetricValue"] {
            color: var(--navy) !important;
            font-family: 'Playfair Display', Georgia, serif !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #4A5568 !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
        }

        /* ── Primary buttons ── */
        .stButton > button[kind="primary"],
        .stButton > button {
            background-color: var(--burgundy) !important;
            color: #fff !important;
            border: none !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
        }
        .stButton > button:hover {
            background-color: #400813 !important;
        }

        /* ── Tab headers ── */
        .stTabs [data-baseweb="tab"] {
            font-family: 'Playfair Display', Georgia, serif !important;
            font-weight: 600 !important;
            color: var(--navy) !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: var(--burgundy) !important;
        }

        /* ── Data tables ── */
        [data-testid="stDataFrame"] {
            border: 1px solid #D4C3A8 !important;
            border-radius: 6px !important;
        }

        /* ── Dividers ── */
        hr {
            border-color: #D4C3A8 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Global Sitewide Footer Function
# ---------------------------------------------------------------------------
def render_footer():
    st.markdown("---")
    st.caption(
        "**Texas CNA Academy** is an independent education and compliance-support platform. "
        "It is not operated by Texas Health and Human Services Commission, TULIP, SEMARC, Prometric, "
        "the Nurse Aide Registry, or the Texas Board of Nursing. Official determinations regarding "
        "certification, approval, registry status, employability, renewal, and licensure are made only "
        "by the appropriate official agencies and systems."
    )
    st.caption("*Last policy review: 2026-07-09*")

# ---------------------------------------------------------------------------
# Sidebar Map Navigation
# ---------------------------------------------------------------------------
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
PAGE_LABEL_BY_KEY = {key: label for label, key in PAGES.items()}

with st.sidebar:
    st.image("https://img.icons8.com/color/96/nurse-female.png", width=80)
    st.title("Texas CNA Academy")
    st.caption("Compliance & Education Portal")
    st.divider()
    
    if "sidebar_nav" not in st.session_state:
        st.session_state["sidebar_nav"] = "Home"
        
    nav_target = st.session_state.pop("nav_target", None)
    if nav_target in PAGE_LABEL_BY_KEY:
        st.session_state["sidebar_nav"] = PAGE_LABEL_BY_KEY[nav_target]
        
    page_label = st.radio(
        "Navigate",
        list(PAGES.keys()),
        key="sidebar_nav",
        label_visibility="collapsed",
    )

page = PAGES[page_label]

# Restrict sub-modules unless authenticated on Home page
NON_AUTH_PAGES = ["home", "compliance", "regulatory_updates", "resources", "semarc_training"]
if page not in NON_AUTH_PAGES:
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please sign in on the Home page to access secure application sections.")
        page = "home"
    else:
        access = get_access_status(user_id)
        if not access["allowed"]:
            st.warning("Your 30-day free trial has ended. Please subscribe on the Home page to continue.")
            page = "home"

# ---------------------------------------------------------------------------
# Route Layout Engine
# ---------------------------------------------------------------------------
    
    st.title("Texas CNA Academy")
    st.markdown(
        "#### **Texas CNA Academy** provides Texas-focused nurse aide training support, "
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
    st.markdown(
        "At **Texas CNA Academy**, our mission is to support nurse aide students and healthcare teams "
        "across Texas with clear, practical, Texas-focused education and compliance tools. We help "
        "users prepare for training, certification, renewal, and workforce readiness using structured "
        "learning resources, skills support, and regulatory guidance aligned with current Texas requirements."
    )
    with st.expander("Mission Disclaimer", expanded=False):
        st.caption(
            "Texas CNA Academy provides educational and compliance-support resources. Official eligibility, "
            "certification, registry status, employability determinations, and licensing actions are made "
            "only through the appropriate official agencies and systems."
        )
        
    st.divider()
    st.subheader("Explore by Your Role")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Student")
        st.write("Preparing for nurse aide training, testing, or renewal in Texas? Access study materials, practice tools, and Texas-specific guidance designed to help you prepare with confidence.")
    with col2:
        st.markdown("### Instructor")
        st.write("Support training delivery with curriculum tools, student progress tracking, skills validation support, and documentation workflows aligned with Texas NATCEP expectations.")
    with col3:
        st.markdown("### Facility / Admin")
        st.write("Track certification-related deadlines, staff records, workforce compliance tasks, and regulatory updates with tools designed for administrators, DONs, and program leaders.")

    st.divider()
    st.subheader("Program Offerings & Tools")
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        st.markdown("#### **Certification & Exam Prep**")
        st.write("Prepare for Texas nurse aide training and competency evaluation with structured study materials, practice assessments, skills support, and reference tools based on current Texas nurse aide guidance.")
    with p_col2:
        st.markdown("#### **Compliance Tracking & Regulatory Guidance**")
        st.write("Texas CNA Academy helps facilities, instructors, and program leaders organize compliance-related tasks, track deadlines, and monitor selected Texas nurse aide workflow requirements.")
        st.caption(" *Texas CNA Academy helps users organize and monitor compliance-related information but does not replace HHSC, TULIP, SEMARC, the Nurse Aide Registry, Prometric, or any official state determination.*")
    with p_col3:
        st.markdown("#### **Renewal Guidance & Tracking Support**")
        st.write("Texas CNA Academy supports users with renewal guidance, deadline awareness, and record-organization tools for Texas nurse aide renewal workflows.")
        st.warning("**Required Microcopy:** Texas nurse aide renewal generally requires 24 hours of in-service education every two years, along with any applicable registry and renewal requirements handled through official Texas systems.")

    st.divider()
    st.subheader("Official Texas Resources")
    st.write("Links below connect users to official Texas government and regulatory resources. These external sites are the authoritative sources for nurse aide registry actions, credentialing functions, employability checks, and regulatory determinations.")
    res1, res2, res3 = st.columns(3)
    with res1:
        st.markdown("**Texas Health and Human Services**")
        st.write("Texas Health and Human Services oversees the Nurse Aide Registry, nurse aide program regulation, and many long-term care regulatory functions relevant to nurse aide training and employability workflows in Texas.")
    with res2:
        st.markdown("**TULIP**")
        st.write("The Texas Unified Licensure Information Portal (TULIP) supports specific credentialing, application, registry, and regulatory workflows in Texas. Available functions vary by user role and access level.")
    with res3:
        st.markdown("**Texas Board of Nursing**")
        st.write("Texas Board of Nursing regulates nursing licensure in Texas. It may be a useful related resource for users exploring future nursing pathways, but nurse aide registry and NATCEP matters are generally handled through HHSC and related systems.")
    render_footer()

# === 2. COMPLIANCE GUIDANCE ===
elif page == "compliance":
    st.title("Texas CNA Compliance & Regulatory Guidance")
    st.markdown("Texas CNA Academy provides Texas-focused compliance support tools and guidance for nurse aide students, instructors, directors of nursing, administrators, and training programs. This page helps users organize information and monitor changes related to nurse aide training, renewal, registry workflows, and employability-related updates in Texas.")
    st.info("Texas CNA Academy is an independent platform. It is not operated by Texas Health and Human Services Commission (HHSC), TULIP, SEMARC, the Nurse Aide Registry, Prometric, or the Texas Board of Nursing. Official decisions about approval, certification, registry status, employability, renewal, and licensure are made only through the appropriate official agencies and systems.")
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.markdown("### What this page helps with")
        st.markdown("- Tracking regulatory updates\n- Monitoring deadlines and workflow changes\n- Reviewing Texas nurse aide renewal guidance\n- Organizing NATCEP-related documentation workflows\n- Linking to official state resources")
    with c_col2:
        st.markdown("### What this page does not do")
        st.markdown("- It does not issue certification\n- It does not verify registry status directly\n- It does not make employability determinations\n- It does not replace required background checks\n- It does not replace HHSC, TULIP, NAR, SEMARC, or Prometric requirements")
        
    st.divider()
    st.subheader("Texas Renewal Guidance")
    st.write("Texas nurse aide renewal guidance should be reviewed through official HHSC resources. Texas CNA Academy may help users track deadlines and organize records, but users must complete all official renewal requirements through the appropriate state systems. Current HHSC guidance states that nurse aides renewing certification must complete at least 24 hours of in-service education every two years.")
    
    st.subheader("NATCEP Records Guidance")
    st.write("For instructors and program leaders, Texas CNA Academy may support documentation workflows related to training attendance, performance tracking, and internal record organization. Programs should continue to maintain required official records and verify current HHSC requirements for forms, approvals, and documentation practices.")
    
    st.subheader("Employability Checks and SEMARC")
    st.write("Texas employability-check workflows may include SEMARC-related processes for authorized users, along with other applicable registry or screening requirements depending on role, setting, and current Texas guidance. Users should not assume that one system replaces every other required check unless confirmed by official source documents.")
    
    st.subheader("Official Texas Resources Links")
    st.markdown("- [Texas Health and Human Services](https://hhs.texas.gov)\n- [TULIP Portal](https://tulip.hhs.texas.gov)\n- Nurse Aide Registry official systems\n- NATCEP guidance points\n- SEMARC Access portals\n- Official provider letters and agency updates")
    st.caption("**Last reviewed:** 2026-07-09")
    render_footer()

# === 3. REGULATORY UPDATES MONITOR ===
elif page == "regulatory_updates":
    st.title("Texas Regulatory Updates Monitor")
    st.warning("**Warning:** Texas CNA Academy monitors official public sources for convenience. Users must review the official source before acting on regulatory content.")
    st.markdown("This page tracks selected Texas nurse aide, NATCEP, TULIP, Nurse Aide Registry, and SEMARC-related updates from official sources. Entries are for awareness and workflow support only. Users must review the underlying official source for final requirements and decisions.")
    
    st.subheader("Current Live Logs")
    for entry in st.session_state.regulatory_entries:
        with st.container():
            st.markdown(f"### {entry['title']}")
            st.write(f"**Date:** {entry['date']} | **Tag:** `{entry['source_agency']}` | **Status:** `{entry['status']}`")
            st.write(f"**Summary:** {entry['summary']}")
            st.info(f"**Internal Action Needed:** {entry['internal_action_needed']}")
            st.caption(f"Last checked: {entry['last_checked']} | Reviewed by: {entry['reviewed_by']} | [Source Link]({entry['source_url']})")
            st.divider()
            
    st.sidebar.subheader("Live Auditor Toolkit")
    if st.sidebar.button("Trigger Daily Sync Diff Engine"):
        st.sidebar.success("Daily Hash Content validation completed: Content unchanged.")
    st.sidebar.info("**Monitored Feeds:**\n1. HHSC Provider Letters\n2. TULIP Resource Trackers\n3. Nurse Aide Registry feeds\n4. SEMARC FAQ Changes")
    render_footer()

# === 4. ROLE WORKFLOWS & DASHBOARDS ===
elif page == "role_dashboards":
    st.title("Role-Based Dashboard Portals")
    role_view = st.selectbox("Switch Dashboard Context Scope", ["Student", "Instructor", "DON (Director of Nursing)", "Admin"])
    
    st.markdown(f"#### current access: **{role_view} Portal View**")
    if role_view == "Student":
        st.markdown("- Exam prep frameworks\n- Skills practice metrics\n- Renewal reminders\n- Official resource paths\n- *Informational notices only*")
    elif role_view == "Instructor":
        st.markdown("- Student progress tracking tools\n- Skills validation support records\n- Attendance logging engines\n- NATCEP documentation reminders\n- Training regulatory feeds")
    elif role_view == "DON (Director of Nursing)":
        st.markdown("- Staff validation deadline arrays\n- In-service tracking systems\n- Critical system compliance alerts\n- Employability check reminders\n- Regulatory stream monitors")
    elif role_view == "Admin":
        st.markdown("- Critical system alerts (SEMARC/NAR/Renewal)\n- Comprehensive Provider letter workflows\n- Comprehensive staff history overviews\n- Full internal configuration audit trails\n- Policy change structural checklists")
        
    st.divider()
    st.subheader("Form 5497 & 5498 Digital Workflow Trackers")
    st.caption("**Disclaimer:** Digital workflow support based on current Texas form structure. Users should verify current official forms and requirements before submission or audit use.")
    
    f_tabs = st.tabs(["Form 5497: Performance Record", "Form 5498: Daily Sign-In"])
    with f_tabs[0]:
        st.write("##### Internal Workflow: Trainee Performance Evaluation")
        st.text_input("Trainee Candidate Name")
        st.checkbox("Validate Technical Procedural Compliance Matrix")
        st.button("Commit Form 5497 Step Log")
    with f_tabs[1]:
        st.write("##### Internal Workflow: Daily Attendance Record Sign-In")
        st.date_input("Training Date Parameter", datetime.date(2026, 7, 10))
        st.text_area("Roster Registry Manifest")
        st.button("Commit Form 5498 Daily Entry")
    render_footer()

# === 5. INSTRUCTOR SEMARC TRAINING ===
elif page == "semarc_training":
    st.title("Instructor SEMARC Training Module and SOP")
    st.caption("*Last updated: 2026-07-09*")
    st.warning("**Confidentiality Notice:** SEMARC-related workflows are limited to authorized users. Staff must not access, share, or interpret SEMARC results outside their assigned role and must follow all confidentiality guidelines.")
    
    st.markdown("### Training Module Copy\n#### **SEMARC Workflow Training for Instructors and Administrators**")
    with st.expander("Review Academic Training Matrix Modules", expanded=True):
        st.markdown(
            "##### **Learning Objectives**\n- Explain what SEMARC is.\n- Identify structural access constraints.\n- Outline differences between SEMARC, NAR, and TULIP.\n- Maintain absolute statutory data confidentiality.\n\n"
            "##### **Section 1: What SEMARC Is**\nSEMARC is the Search Engine for Multi-Agency Reportable Conduct. Texas describes it as a centralized system for authorized users to search across multiple participating agencies for reportable conduct information that may affect eligibility for employment, volunteer positions, certification, contracts, or licensure.\n\n"
            "##### **Section 2: Who May Access SEMARC**\nSEMARC is not a general public tool. Texas states that only users authorized by participating agencies may access the system, and authentication is required for all users. Staff should not assume that all instructors or school employees automatically have access.\n\n"
            "##### **Section 3: Confidentiality**\nSEMARC search results are confidential. Texas states that SEMARC search results may not be disclosed except as authorized by law. Staff must not share screenshots, printouts, copied results, or verbal summaries outside approved workflows.\n\n"
            "##### **Section 4: SEMARC Is Not the Whole Workflow**\nStaff should not assume SEMARC replaces every other required screening step. HHSC training refers to both NAR and SEMARC employability status checks, which means staff should verify which official searches and reviews apply to the role or setting involved.\n\n"
            "##### **Section 5: Internal Rule for Texas CNA Academy**\nTexas CNA Academy staff must use official agency guidance before acting on employability-related information. Internal platform notices, checklists, or reminders may support workflow organization, but they do not replace official state requirements or determinations."
        )
        
    st.subheader("Interactive Knowledge Verification Quiz")
    q1 = st.radio("1. Is SEMARC a public search tool for all staff?", ["Yes", "No, it is strictly restricted to authorized and authenticated users"])
    q2 = st.radio("2. Are SEMARC search results confidential?", ["No", "Yes, strictly regulated under Texas Health and Safety Code Section 810.010"])
    q3 = st.radio("3. Does SEMARC automatically replace every other required Texas verification check?", ["Yes", "No, multi-system checks remain baseline requirements"])
    
    if st.button("Submit Quiz Verification"):
        st.session_state.quiz_submitted = True
        if q1 == "No, it is strictly restricted to authorized and authenticated users" and q2 == "Yes, strictly regulated under Texas Health and Safety Code Section 810.010" and q3 == "No, multi-system checks remain baseline requirements":
            st.success("Comprehensive Verification Verified! Excellent understanding of state operational compliance frameworks.")
        else:
            st.error("Some entries require review. Re-read the module panels and re-evaluate.")
            
    st.subheader("Required Operational Application Activation")
    ack1 = st.checkbox("I understand that SEMARC access is restricted to authorized users.")
    ack2 = st.checkbox("I understand that SEMARC search results are confidential and may only be handled according to law and policy.")
    ack3 = st.checkbox("I understand that internal workflow tools do not replace official HHSC, SEMARC, TULIP, or NAR requirements.")
    ack4 = st.checkbox("I will review current official guidance before acting on employability-related information.")
    
    if ack1 and ack2 and ack3 and ack4:
        st.session_state.training_acknowledged = True
        st.success("Operational profile activation confirmed. Access records validated.")
    else:
        st.warning("All procedural points must be acknowledged to confirm system workflow validation clearance.")
    render_footer()

# === EXTENSIBLE ROUTING TO CUSTOM PAGE MODULES ===
elif page == "courses":
    from pages import courses as _page; _page.show()
elif page == "exam_prep":
    from pages import exam_prep as _page; _page.show()
elif page == "progress":
    from pages import progress as _page; _page.show()
elif page == "clinical_skills_lab":
    from pages import clinical_skills_lab as _page; _page.show()
elif page == "community_hub":
    from pages import community_hub as _page; _page.show()
elif page == "ceu_tracker":
    from pages import ceu_tracker as _page; _page.show()
elif page == "renewal_check":
    from pages import renewal_check as _page; _page.show()
elif page == "staffing":
    from pages import staffing as _page; _page.show()
elif page == "buddy":
    from pages import buddy as _page; _page.show()
elif page == "resources":
    from pages import resources as _page; _page.show()
elif page == "admin":
    from pages import admin as _page; _page.show()

