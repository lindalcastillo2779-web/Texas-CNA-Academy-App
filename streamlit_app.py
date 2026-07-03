"""
Texas CNA Academy (TULIP-Link)
================================
Main entry-point for the Streamlit multi-page application.

Sections
--------
• 🏠 Home          – Welcome / self-registration
• 🎓 Courses       – NATCEP study roadmap and module content
• 📚 Exam Prep     – Practice quizzes (NATCEP domains)
• 🧪 Clinical Skills Lab – Interactive Prometric-aligned skill simulations
• 📋 CEU Tracker   – Log & track continuing-education hours
• ✅ Renewal Check – Renewal readiness summary
• 🏥 Staffing      – Facility staffing compliance log
• 🤖 Buddy         – AI study and compliance chatbot
• 🔧 Admin         – Admin-only management panel
"""

import streamlit as st

from db import init_db

# ---------------------------------------------------------------------------
# Initialise database on first run
# ---------------------------------------------------------------------------
init_db()

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Texas CNA Academy",
    page_icon="🎓",
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
    "🏠 Home": "home",
    "🎓 Courses": "courses",
    "📚 Exam Prep": "exam_prep",
    "🧪 Clinical Skills Lab": "clinical_skills_lab",
    "📋 CEU Tracker": "ceu_tracker",
    "✅ Renewal Check": "renewal_check",
    "🏥 Staffing Log": "staffing",
    "🤖 Buddy": "buddy",
    "🔧 Admin Panel": "admin",
}

with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/nurse-female.png",
        width=80,
    )
    st.title("Texas CNA Academy")
    st.caption("TULIP-Link Portal")
    st.divider()
    page_label = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

page = PAGES[page_label]

# ---------------------------------------------------------------------------
# Route to individual page modules
# ---------------------------------------------------------------------------
if page == "home":
    from pages import home as _page
elif page == "courses":
    from pages import courses as _page
elif page == "exam_prep":
    from pages import exam_prep as _page
elif page == "clinical_skills_lab":
    from pages import clinical_skills_lab as _page
elif page == "ceu_tracker":
    from pages import ceu_tracker as _page
elif page == "renewal_check":
    from pages import renewal_check as _page
elif page == "staffing":
    from pages import staffing as _page
elif page == "buddy":
    from pages import buddy as _page
elif page == "admin":
    from pages import admin as _page
else:
    from pages import home as _page

_page.show()
