"""Community Hub – mentor matching, study groups, and workforce opportunities."""

from __future__ import annotations

import streamlit as st

from db import (
    create_community_post,
    get_community_dashboard_counts,
    get_community_posts,
    get_community_profile,
    get_mentor_matches,
    get_recommended_community_actions,
    get_recommended_posts_for_user,
    get_staff_demand_summary,
    get_user_by_id,
    get_user_community_posts,
    upsert_community_profile,
)
from utils.media import render_page_media

POST_TYPE_LABELS = {
    "mentor_request": "Mentor Request",
    "mentor_offer": "Mentor Offer",
    "study_group": "Study Group",
    "practice_partner": "Practice Partner",
    "opportunity": "Opportunity",
}
ROLE_OPTIONS = ["student", "cna", "don", "instructor", "facility"]


def show() -> None:
    st.title("🤝 Community Mentor + Workforce Hub")
    st.caption(
        "Connect students, CNAs, instructors, DONs, and facilities through mentoring, "
        "study support, practice partnerships, and local opportunities."
    )
    render_page_media("community_hub")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please **sign in** on the Home page to join the community hub.")
        return

    user = get_user_by_id(user_id)
    if not user:
        st.error("We could not load your account. Please sign in again.")
        return

    counts = get_community_dashboard_counts()
    recommendations = get_recommended_community_actions(user_id)
    mentor_matches = get_mentor_matches(user_id)
    recommended_posts = get_recommended_posts_for_user(user_id)
    profile = get_community_profile(user_id) or {}

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mentors Available", counts["mentors"])
    col2.metric("Study Groups", counts["study_groups"])
    col3.metric("Opportunities", counts["opportunities"])
    col4.metric("Active Posts", counts["active_posts"])

    st.divider()
    tabs = st.tabs(["My Profile", "Mentor Matches", "Community Board", "Opportunity Board"])

    with tabs[0]:
        _render_profile_tab(user_id, user["role"], profile)

    with tabs[1]:
        _render_matches_tab(recommendations, mentor_matches, recommended_posts)

    with tabs[2]:
        _render_board_tab(user_id, user["role"])

    with tabs[3]:
        _render_opportunities_tab(recommended_posts)


def _render_profile_tab(user_id: int, role: str, profile: dict) -> None:
    st.subheader("Your Community Profile")
    st.write(
        "Tell the community how you want to participate so the app can recommend mentors, "
        "study circles, and workforce opportunities that fit your goals."
    )

    current_audiences = _split_csv(profile.get("interest_areas"))
    with st.form("community_profile_form"):
        city = st.text_input("City or region", value=profile.get("city", ""))
        organization = st.text_input(
            "School, employer, or organization",
            value=profile.get("organization", ""),
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            can_mentor = st.checkbox(
                "I can mentor others",
                value=bool(profile.get("can_mentor", 0)),
            )
        with col2:
            wants_mentor = st.checkbox(
                "I want a mentor",
                value=bool(profile.get("wants_mentor", 1 if role == "student" else 0)),
            )
        with col3:
            open_to_opportunities = st.checkbox(
                "Show me workforce opportunities",
                value=bool(profile.get("open_to_opportunities", 1)),
            )
        interests = st.multiselect(
            "Interest areas",
            options=[
                "exam prep",
                "infection control",
                "safety and emergency",
                "clinical skills",
                "communication",
                "renewal",
                "ceu",
                "staffing",
                "job search",
                "mentoring",
            ],
            default=current_audiences,
        )
        availability = st.text_input(
            "Availability",
            value=profile.get("availability", ""),
            placeholder="Example: Weeknights after 6 PM or Saturdays",
        )
        bio = st.text_area(
            "Short bio",
            value=profile.get("bio", ""),
            placeholder="Share the support you need or the experience you can offer.",
        )
        submitted = st.form_submit_button("Save Community Profile")

    if submitted:
        upsert_community_profile(
            user_id=user_id,
            city=city,
            organization=organization,
            can_mentor=can_mentor,
            wants_mentor=wants_mentor,
            open_to_opportunities=open_to_opportunities,
            interest_areas=", ".join(interests),
            availability=availability,
            bio=bio,
        )
        st.success("Your community profile is saved.")
        st.rerun()

    st.divider()
    st.subheader("Your Recent Posts")
    my_posts = get_user_community_posts(user_id)
    if not my_posts:
        st.info("You have not posted yet. Add a mentor request, study group, or opportunity below.")
        return
    for post in my_posts:
        _render_post_card(post, show_author=False)


def _render_matches_tab(
    recommendations: list[str],
    mentor_matches: list[dict],
    recommended_posts: list[dict],
) -> None:
    st.subheader("Recommended Next Steps")
    for rec in recommendations:
        st.success(rec)

    st.divider()
    st.subheader("Mentor Matches")
    if not mentor_matches:
        st.info(
            "No mentor profiles match you yet. Complete your profile and invite instructors, CNAs, or DONs to opt in."
        )
    else:
        for mentor in mentor_matches:
            with st.container(border=True):
                st.markdown(f"**{mentor['name']}** · {mentor['role'].upper()}")
                details = [mentor.get("organization", "").strip(), mentor.get("city", "").strip()]
                st.caption(" · ".join(item for item in details if item))
                if mentor.get("interest_areas"):
                    st.write(f"**Focus areas:** {mentor['interest_areas']}")
                if mentor.get("availability"):
                    st.write(f"**Availability:** {mentor['availability']}")
                if mentor.get("bio"):
                    st.write(mentor["bio"])

    st.divider()
    st.subheader("Recommended Posts")
    if not recommended_posts:
        st.info("The board is still warming up. Create a post to attract replies from the community.")
        return
    for post in recommended_posts[:4]:
        _render_post_card(post)


def _render_board_tab(user_id: int, role: str) -> None:
    st.subheader("Create a Community Post")
    with st.form("community_post_form"):
        post_type = st.selectbox(
            "Post type",
            options=list(POST_TYPE_LABELS.keys()),
            format_func=lambda key: POST_TYPE_LABELS[key],
        )
        title = st.text_input("Title *")
        description = st.text_area(
            "Description *",
            placeholder="What support, practice, or opportunity are you offering or requesting?",
        )
        location = st.text_input("Location")
        contact_info = st.text_input(
            "Preferred contact details",
            placeholder="Optional phone, email, or instructions for responding",
        )
        tags = st.text_input(
            "Tags",
            placeholder="Example: exam prep, transfer, ceu, hiring",
        )
        audience_roles = st.multiselect(
            "Who should see this?",
            options=ROLE_OPTIONS,
            default=[role],
        )
        submitted = st.form_submit_button("Publish Post")

    if submitted:
        if not title.strip() or not description.strip():
            st.warning("Title and description are required.")
        else:
            create_community_post(
                user_id=user_id,
                post_type=post_type,
                title=title,
                description=description,
                location=location,
                contact_info=contact_info,
                tags=tags,
                audience_roles=",".join(audience_roles),
            )
            st.success("Your post is live on the community board.")
            st.rerun()

    st.divider()
    filter_options = ["all"] + list(POST_TYPE_LABELS.keys())
    selected_filter = st.selectbox(
        "Filter board",
        options=filter_options,
        format_func=lambda key: "All Posts" if key == "all" else POST_TYPE_LABELS[key],
    )
    posts = get_community_posts(
        post_type=None if selected_filter == "all" else selected_filter,
        status="active",
    )
    if not posts:
        st.info("No posts match this filter yet.")
        return
    for post in posts:
        _render_post_card(post)


def _render_opportunities_tab(recommended_posts: list[dict]) -> None:
    st.subheader("Opportunity Feed")
    opportunity_posts = [post for post in recommended_posts if post["post_type"] == "opportunity"]
    if not opportunity_posts:
        opportunity_posts = get_community_posts(post_type="opportunity", status="active")

    if opportunity_posts:
        for post in opportunity_posts:
            _render_post_card(post)
    else:
        st.info("No opportunity posts yet. Facilities and instructors can publish openings from the board.")

    st.divider()
    st.subheader("Active Facilities Snapshot")
    staff_summary = get_staff_demand_summary()
    if not staff_summary:
        st.info("No staffing demand records yet. When facilities log shifts, the hub will highlight active sites.")
        return
    for facility in staff_summary:
        with st.container(border=True):
            st.markdown(f"**{facility['facility_name']}**")
            st.write(
                f"Shifts logged: **{facility['shifts_logged']}** · "
                f"Latest activity: **{facility['latest_shift_date']}**"
            )
            if facility["non_compliant_shifts"]:
                st.warning(
                    f"{facility['non_compliant_shifts']} non-compliant shift(s) logged — this may signal strong demand for support."
                )
            else:
                st.success("Recent staffing records are compliant.")


def _render_post_card(post: dict, show_author: bool = True) -> None:
    with st.container(border=True):
        st.markdown(f"**{POST_TYPE_LABELS.get(post['post_type'], post['post_type'])}**")
        st.subheader(post["title"])
        if show_author:
            author_name = post.get("author_name") or "Texas CNA Academy"
            author_role = post.get("author_role") or "community"
            st.caption(f"Posted by {author_name} · {str(author_role).upper()}")
        st.write(post["description"])
        meta = []
        if post.get("location"):
            meta.append(f"📍 {post['location']}")
        if post.get("tags"):
            meta.append(f"🏷️ {post['tags']}")
        if meta:
            st.write(" · ".join(meta))
        if post.get("contact_info"):
            st.info(f"Contact: {post['contact_info']}")


def _split_csv(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]
