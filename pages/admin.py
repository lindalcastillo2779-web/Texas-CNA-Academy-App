"""Admin panel – requires ADMIN_SECRET authentication."""

import pandas as pd
import streamlit as st

import db
from auth import require_admin
from utils.media import render_page_media


def show() -> None:
    st.title("🔧 Admin Panel")
    render_page_media("admin")

    if not require_admin():
        st.info("Enter your admin password in the **sidebar** to access this panel.")
        return

    st.success("✅ Authenticated as administrator")

    tab_users, tab_questions, tab_quiz_log, tab_community, tab_db = st.tabs(
        ["👥 Users", "❓ Questions", "📊 Quiz Log", "🤝 Community", "🗄️ Database"]
    )

    # ------------------------------------------------------------------ Users
    with tab_users:
        st.subheader("Registered Users")
        with db.get_conn() as conn:
            users = [dict(r) for r in conn.execute(
                """SELECT id, name, email, role, state_id, subscription_active, created_at
                   FROM users ORDER BY created_at DESC"""
            ).fetchall()]
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
            user_label_by_id = {
                u["id"]: f"{u['name']} ({u['email']})"
                for u in users
            }
            selected_user_id = st.selectbox(
                "Select user for subscription update",
                options=[u["id"] for u in users],
                format_func=lambda uid: user_label_by_id[uid],
            )
            selected_user = next((u for u in users if u["id"] == selected_user_id), None)
            if selected_user:
                is_active = st.checkbox(
                    "Subscription active",
                    value=bool(selected_user["subscription_active"]),
                    key=f"sub_active_{selected_user_id}",
                )
                if st.button("Save subscription status", key="save_subscription_status"):
                    db.set_subscription_active(selected_user_id, is_active)
                    st.success("Subscription status updated.")
                    st.rerun()
        else:
            st.info("No users registered yet.")

    # ------------------------------------------------------------ Questions
    with tab_questions:
        st.subheader("Exam Questions")
        with db.get_conn() as conn:
            qs = [dict(r) for r in conn.execute(
                "SELECT id, domain, question, correct FROM exam_questions ORDER BY domain"
            ).fetchall()]
        if qs:
            st.dataframe(pd.DataFrame(qs), use_container_width=True, hide_index=True)

        st.subheader("Add a Question")
        with st.form("add_question_form"):
            q_domain  = st.text_input("Domain")
            q_text    = st.text_area("Question text")
            q_a       = st.text_input("Option A")
            q_b       = st.text_input("Option B")
            q_c       = st.text_input("Option C")
            q_d       = st.text_input("Option D")
            q_correct = st.selectbox("Correct answer", ["A", "B", "C", "D"])
            q_expl    = st.text_area("Explanation (optional)")
            add_q     = st.form_submit_button("Add Question")

        if add_q:
            if not all([q_domain, q_text, q_a, q_b, q_c, q_d]):
                st.warning("All fields except explanation are required.")
            else:
                with db.get_conn() as conn:
                    conn.execute(
                        """INSERT INTO exam_questions
                           (domain, question, option_a, option_b, option_c, option_d,
                            correct, explanation)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (q_domain, q_text, q_a, q_b, q_c, q_d, q_correct, q_expl),
                    )
                st.success("Question added.")
                st.rerun()

    # ------------------------------------------------------------ Quiz log
    with tab_quiz_log:
        st.subheader("Quiz Attempt History")
        with db.get_conn() as conn:
            rows = [dict(r) for r in conn.execute(
                """SELECT qa.id, u.name, u.email, qa.domain,
                          qa.score, qa.total,
                          ROUND(CAST(qa.score AS REAL)/qa.total*100, 1) AS pct,
                          qa.taken_at
                   FROM quiz_attempts qa
                   LEFT JOIN users u ON u.id = qa.user_id
                   ORDER BY qa.taken_at DESC LIMIT 100"""
            ).fetchall()]
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No quiz attempts recorded yet.")

    # -------------------------------------------------------- Community hub
    with tab_community:
        st.subheader("Community Hub Moderation")
        counts = db.get_community_dashboard_counts()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mentors", counts["mentors"])
        col2.metric("Mentees", counts["mentees"])
        col3.metric("Study Groups", counts["study_groups"])
        col4.metric("Active Posts", counts["active_posts"])

        profiles = db.list_community_profiles(limit=100)
        if profiles:
            st.markdown("**Active community profiles**")
            profile_df = pd.DataFrame(profiles)[
                ["name", "role", "city", "organization", "can_mentor", "wants_mentor", "open_to_opportunities", "interest_areas", "availability"]
            ]
            profile_df.columns = [
                "Name",
                "Role",
                "City",
                "Organization",
                "Mentor",
                "Wants Mentor",
                "Open to Opportunities",
                "Interest Areas",
                "Availability",
            ]
            st.dataframe(profile_df, use_container_width=True, hide_index=True)
        else:
            st.info("No community profiles yet.")

        posts = db.get_community_posts(status=None, limit=200)
        st.markdown("**Community posts**")
        if posts:
            post_df = pd.DataFrame(posts)[
                ["id", "post_type", "title", "author_name", "author_role", "location", "status", "created_at"]
            ]
            post_df.columns = ["ID", "Type", "Title", "Author", "Role", "Location", "Status", "Created"]
            st.dataframe(post_df, use_container_width=True, hide_index=True)

            post_ids = [post["id"] for post in posts]
            selected_post_id = st.selectbox("Select post to moderate", options=post_ids)
            selected_post = next((post for post in posts if post["id"] == selected_post_id), None)
            if selected_post:
                st.write(selected_post["description"])
                new_status = st.selectbox(
                    "Status",
                    options=["active", "archived"],
                    index=0 if selected_post["status"] == "active" else 1,
                    key=f"community_status_{selected_post_id}",
                )
                if st.button("Save post status", key=f"save_community_status_{selected_post_id}"):
                    db.set_community_post_status(selected_post_id, new_status)
                    st.success("Community post updated.")
                    st.rerun()
        else:
            st.info("No community posts recorded yet.")

    # ---------------------------------------------------------- Database info
    with tab_db:
        st.subheader("Database Info")
        st.code(f"DB_PATH = {db.DB_PATH}")
        _KNOWN_TABLES = frozenset(
            [
                "users",
                "ceu_records",
                "exam_questions",
                "quiz_attempts",
                "staff_records",
                "community_profiles",
                "community_posts",
            ]
        )
        with db.get_conn() as conn:
            for table in sorted(_KNOWN_TABLES):
                if table not in _KNOWN_TABLES:
                    continue
                count = conn.execute(
                    f"SELECT COUNT(*) FROM {table}"  # noqa: S608 – table is whitelisted above
                ).fetchone()[0]
                st.write(f"**{table}**: {count} rows")
