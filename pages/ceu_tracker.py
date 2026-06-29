"""CEU Tracker – log and view continuing-education hours."""

import datetime

import pandas as pd
import streamlit as st

from db import add_ceu_record, get_ceu_records, total_ceu_hours

# Texas CNA renewal: 24 CEU hours per 2-year cycle
RENEWAL_HOURS_REQUIRED = 24.0


def show() -> None:
    st.title("📋 CEU Tracker")
    st.caption("Track your continuing-education hours toward CNA renewal")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please **sign in** on the Home page to track your CEUs.")
        return

    earned = total_ceu_hours(user_id)
    remaining = max(0.0, RENEWAL_HOURS_REQUIRED - earned)

    col1, col2, col3 = st.columns(3)
    col1.metric("Hours Earned", f"{earned:.1f}")
    col2.metric("Hours Required", f"{RENEWAL_HOURS_REQUIRED:.0f}")
    col3.metric("Hours Remaining", f"{remaining:.1f}")

    progress = min(1.0, earned / RENEWAL_HOURS_REQUIRED)
    st.progress(progress, text=f"{progress*100:.0f}% complete")

    st.divider()

    # Log a new CEU
    with st.expander("➕ Log a completed course", expanded=False):
        with st.form("ceu_form"):
            course  = st.text_input("Course / Training name *")
            provider = st.text_input("Provider / Institution")
            hours   = st.number_input("Hours completed *", min_value=0.5, max_value=40.0,
                                       value=1.0, step=0.5)
            date    = st.date_input("Completion date *",
                                    value=datetime.date.today(),
                                    max_value=datetime.date.today())
            cert    = st.text_input("Certificate number (optional)")
            save    = st.form_submit_button("Save CEU Record")

        if save:
            if not course:
                st.warning("Course name is required.")
            else:
                add_ceu_record(
                    user_id,
                    course.strip(),
                    provider.strip(),
                    float(hours),
                    str(date),
                    cert.strip(),
                )
                st.success(f"✅ Logged {hours:.1f} hours for **{course}**.")
                st.rerun()

    # History
    records = get_ceu_records(user_id)
    if records:
        st.subheader("📂 CEU History")
        df = pd.DataFrame(records)[
            ["completed_on", "course_name", "provider", "hours", "certificate"]
        ]
        df.columns = ["Date", "Course", "Provider", "Hours", "Certificate"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No CEU records yet. Log your first course above!")
