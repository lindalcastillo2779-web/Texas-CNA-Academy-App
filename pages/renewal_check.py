"""Renewal Check – CNA renewal readiness summary."""

import datetime

import streamlit as st

from db import get_ceu_records, total_ceu_hours
from email_utils import send_ceu_reminder

RENEWAL_HOURS_REQUIRED = 24.0
RENEWAL_CYCLE_YEARS    = 2


def show() -> None:
    st.title("✅ Renewal Readiness Check")
    st.caption("Texas CNA 2-year renewal overview")

    user_id   = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name", "")

    if not user_id:
        st.warning("Please **sign in** on the Home page to view your renewal status.")
        return

    # Renewal date (user-supplied)
    st.subheader("When does your CNA certification expire?")
    exp_date = st.date_input(
        "Expiry date",
        value=datetime.date.today() + datetime.timedelta(days=365),
        min_value=datetime.date.today(),
        key="renewal_exp_date",
    )

    days_left = (exp_date - datetime.date.today()).days
    earned    = total_ceu_hours(user_id)
    remaining = max(0.0, RENEWAL_HOURS_REQUIRED - earned)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Days Until Expiry", days_left)
    with col2:
        ceu_status = "✅ Met" if remaining == 0 else f"⚠️ {remaining:.1f} hrs needed"
        st.metric("CEU Status", ceu_status)

    # Overall readiness
    st.subheader("Readiness Summary")
    items = {
        f"CEUs: {earned:.1f}/{RENEWAL_HOURS_REQUIRED:.0f} hours logged": earned >= RENEWAL_HOURS_REQUIRED,
        f"Renewal date set ({exp_date})": True,
        f"Active CNA state registration": None,   # placeholder – user to verify
    }
    for label, status in items.items():
        if status is True:
            st.success(f"✅ {label}")
        elif status is False:
            st.error(f"❌ {label}")
        else:
            st.warning(f"⚠️ {label} – verify with the Texas NA Registry")

    # Email reminder
    if remaining > 0:
        st.divider()
        email_input = st.text_input(
            "Send yourself a reminder email",
            placeholder="your@email.com",
            key="reminder_email",
        )
        if st.button("Send Reminder 📧", key="send_reminder"):
            if not email_input:
                st.warning("Please enter your email address.")
            else:
                ok = send_ceu_reminder(user_name or "CNA Candidate", email_input, remaining)
                if ok:
                    st.success("Reminder email sent!")
                else:
                    st.error("Could not send email – check SMTP configuration.")

    # Recent CEU records summary
    records = get_ceu_records(user_id)
    if records:
        st.divider()
        st.subheader("Recent CEU entries")
        for r in records[:5]:
            st.write(f"• {r['completed_on']}  |  {r['course_name']}  |  **{r['hours']} hrs**")
