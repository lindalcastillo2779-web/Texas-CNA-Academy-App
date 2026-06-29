"""
Texas CNA Academy (TULIP-Link)
================================
Main entry-point for the Streamlit multi-page application.

Sections
--------
• 🏠 Home          – Welcome / self-registration
• 📚 Exam Prep     – Practice quizzes (NATCEP domains)
• 📋 CEU Tracker   – Log & track continuing-education hours
• ✅ Renewal Check – Renewal readiness summary
• 🏥 Staffing      – Facility staffing compliance log
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
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
PAGES = {
    "🏠 Home": "home",
    "📚 Exam Prep": "exam_prep",
    "📋 CEU Tracker": "ceu_tracker",
    "✅ Renewal Check": "renewal_check",
    "🏥 Staffing Log": "staffing",
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
elif page == "exam_prep":
    from pages import exam_prep as _page
elif page == "ceu_tracker":
    from pages import ceu_tracker as _page
elif page == "renewal_check":
    from pages import renewal_check as _page
elif page == "staffing":
    from pages import staffing as _page
elif page == "admin":
    from pages import admin as _page

_page.show()
