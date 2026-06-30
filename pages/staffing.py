"""Staffing Log – facility staffing compliance tracking."""

import datetime

import pandas as pd
import streamlit as st

from db import add_staff_record, get_staff_records

SHIFT_TYPES = ["day", "evening", "night"]


def show() -> None:
    st.title("🏥 Staffing Compliance Log")
    st.caption("Track CNA shift assignments and compliance for your facility")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please **sign in** on the Home page to use the staffing log.")
        return

    # Add a shift record
    with st.expander("➕ Log a shift", expanded=False):
        with st.form("staff_form"):
            facility    = st.text_input("Facility name *")
            cna_name    = st.text_input("CNA full name *")
            cna_id      = st.text_input("CNA state ID / registry #")
            shift_date  = st.date_input("Shift date *", value=datetime.date.today())
            shift_type  = st.selectbox("Shift type *", SHIFT_TYPES)
            hours       = st.number_input("Hours worked *", min_value=1.0,
                                          max_value=16.0, value=8.0, step=0.5)
            compliant   = st.checkbox("Staffing ratio compliant", value=True)
            notes       = st.text_area("Notes (optional)")
            save        = st.form_submit_button("Save Record")

        if save:
            if not facility or not cna_name:
                st.warning("Facility name and CNA name are required.")
            else:
                add_staff_record(
                    facility.strip(),
                    cna_name.strip(),
                    cna_id.strip(),
                    str(shift_date),
                    shift_type,
                    float(hours),
                    compliant,
                    notes.strip(),
                )
                st.success(f"✅ Shift logged for **{cna_name}** at **{facility}**.")
                st.rerun()

    # Filters
    st.subheader("📊 Shift Records")
    records = get_staff_records()
    if not records:
        st.info("No shift records yet. Log the first shift above!")
        return

    df = pd.DataFrame(records)
    facilities = ["All"] + sorted(df["facility_name"].unique().tolist())
    sel_facility = st.selectbox("Filter by facility", facilities)
    if sel_facility != "All":
        df = df[df["facility_name"] == sel_facility]

    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Shifts", len(df))
    col2.metric("Total Hours", f"{df['hours_worked'].sum():.1f}")
    non_compliant = int((df["compliant"] == 0).sum())
    col3.metric("Non-Compliant Shifts", non_compliant,
                delta_color="inverse" if non_compliant > 0 else "off")

    display_cols = ["shift_date", "facility_name", "cna_name", "cna_state_id",
                    "shift_type", "hours_worked", "compliant", "notes"]
    rename_map = {
        "shift_date":    "Date",
        "facility_name": "Facility",
        "cna_name":      "CNA Name",
        "cna_state_id":  "State ID",
        "shift_type":    "Shift",
        "hours_worked":  "Hours",
        "compliant":     "Compliant",
        "notes":         "Notes",
    }
    st.dataframe(
        df[display_cols].rename(columns=rename_map),
        use_container_width=True,
        hide_index=True,
    )
