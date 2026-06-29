"""Admin panel – requires ADMIN_SECRET authentication."""

import pandas as pd
import streamlit as st

import db
from auth import require_admin


def show() -> None:
    st.title("🔧 Admin Panel")

    if not require_admin():
        st.info("Enter your admin password in the **sidebar** to access this panel.")
        return

    st.success("✅ Authenticated as administrator")

    tab_users, tab_questions, tab_quiz_log, tab_db = st.tabs(
        ["👥 Users", "❓ Questions", "📊 Quiz Log", "🗄️ Database"]
    )

    # ------------------------------------------------------------------ Users
    with tab_users:
        st.subheader("Registered Users")
        with db.get_conn() as conn:
            users = [dict(r) for r in conn.execute(
                "SELECT id, name, email, role, state_id, created_at FROM users ORDER BY created_at DESC"
            ).fetchall()]
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
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

    # ---------------------------------------------------------- Database info
    with tab_db:
        st.subheader("Database Info")
        st.code(f"DB_PATH = {db.DB_PATH}")
        _KNOWN_TABLES = frozenset(
            ["users", "ceu_records", "exam_questions", "quiz_attempts", "staff_records"]
        )
        with db.get_conn() as conn:
            for table in sorted(_KNOWN_TABLES):
                if table not in _KNOWN_TABLES:
                    continue
                count = conn.execute(
                    f"SELECT COUNT(*) FROM {table}"  # noqa: S608 – table is whitelisted above
                ).fetchone()[0]
                st.write(f"**{table}**: {count} rows")
