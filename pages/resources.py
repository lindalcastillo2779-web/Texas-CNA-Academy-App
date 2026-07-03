"""Verified Resources page — official Texas agency links."""

import streamlit as st


RESOURCES = [
    {
        "icon": "🏛️",
        "title": "Texas Health and Human Services",
        "description": (
            "The Texas Health and Human Services Commission (HHSC) oversees the Nurse Aide "
            "Registry, long-term care facility regulations, CNA certification, and healthcare "
            "provider compliance in Texas."
        ),
        "url": "https://www.hhs.texas.gov/",
        "label": "Visit Texas HHS",
    },
    {
        "icon": "🏭",
        "title": "TULIP — Nurse Aide Registry",
        "description": (
            "The Texas Unified Licensure Information Portal (TULIP) is the official state system "
            "for verifying nurse aide certifications, checking registry status, and managing "
            "nurse aide records in Texas."
        ),
        "url": "https://vo.licensing.hpc.texas.gov/datamart/main.do",
        "label": "Access TULIP Registry",
    },
    {
        "icon": "💼",
        "title": "Texas Workforce Commission",
        "description": (
            "The Texas Workforce Commission (TWC) supports workforce development, healthcare "
            "career resources, job placement services, and continuing education funding "
            "opportunities for CNAs and healthcare workers."
        ),
        "url": "https://www.twc.texas.gov/",
        "label": "Visit Texas TWC",
    },
    {
        "icon": "📋",
        "title": "Texas Board of Nursing",
        "description": (
            "The Texas Board of Nursing (BON) regulates the nursing profession in Texas, "
            "including licensure, continuing education requirements, and disciplinary standards "
            "for registered nurses, LVNs, and nurse aides."
        ),
        "url": "https://www.bon.texas.gov/",
        "label": "Visit Texas BON",
    },
]


def show() -> None:
    st.title("✅ Verified Resources")
    st.markdown(
        "Official Texas state agency resources for nurse aide students, active CNAs, "
        "instructors, and healthcare facilities. All links connect directly to verified "
        "government and regulatory sites."
    )
    st.divider()

    for resource in RESOURCES:
        with st.container(border=True):
            col_icon, col_content = st.columns([1, 9])
            with col_icon:
                st.markdown(
                    f"<div style='font-size:2.2rem;padding-top:4px'>{resource['icon']}</div>",
                    unsafe_allow_html=True,
                )
            with col_content:
                st.subheader(resource["title"])
                st.write(resource["description"])
                st.link_button(resource["label"], resource["url"])

    st.divider()
    st.info(
        "📌 **Why These Resources Matter** — As a Texas nurse aide, staying connected to "
        "official regulatory agencies ensures you remain compliant, informed, and career-ready. "
        "These agencies set the standards for CNA certification, renewal, and professional "
        "practice across the state of Texas."
    )
