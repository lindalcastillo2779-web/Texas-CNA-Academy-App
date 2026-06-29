"""Exam Prep – NATCEP practice quiz page."""

import streamlit as st

from db import get_domains, get_questions_by_domain, save_quiz_attempt

LETTERS = ["A", "B", "C", "D"]


def show() -> None:
    st.title("📚 Exam Prep – Practice Quiz")
    st.caption("NATCEP-aligned practice questions")

    domains = ["All Domains"] + get_domains()
    selected_domain = st.selectbox("Select a domain", domains)
    num_questions = st.slider("Number of questions", 3, 10, 5)

    if st.button("Start Quiz 🚀", key="start_quiz"):
        questions = get_questions_by_domain(
            None if selected_domain == "All Domains" else selected_domain,
            limit=num_questions,
        )
        if not questions:
            st.warning("No questions available for this domain yet.")
            return
        st.session_state["quiz_questions"] = questions
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_domain"] = selected_domain

    if "quiz_questions" not in st.session_state or not st.session_state["quiz_questions"]:
        st.info("Select a domain and click **Start Quiz** to begin.")
        return

    questions = st.session_state["quiz_questions"]
    answers   = st.session_state["quiz_answers"]
    submitted = st.session_state.get("quiz_submitted", False)

    st.divider()
    for i, q in enumerate(questions):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        opts = {
            "A": q["option_a"],
            "B": q["option_b"],
            "C": q["option_c"],
            "D": q["option_d"],
        }
        saved_answer = answers.get(str(i), "A")
        safe_index = LETTERS.index(saved_answer) if saved_answer in LETTERS else 0
        choice = st.radio(
            f"Q{i+1} options",
            options=list(opts.keys()),
            format_func=lambda k, o=opts: f"{k}) {o[k]}",
            key=f"q_{i}",
            label_visibility="collapsed",
            disabled=submitted,
            index=safe_index,
        )
        answers[str(i)] = choice

        if submitted:
            correct = q["correct"]
            if choice == correct:
                st.success(f"✅ Correct! {q.get('explanation', '')}")
            else:
                st.error(
                    f"❌ Incorrect. The correct answer is **{correct}) {opts[correct]}**. "
                    f"{q.get('explanation', '')}"
                )
        st.divider()

    if not submitted:
        if st.button("Submit Quiz ✔️", key="submit_quiz"):
            score = sum(
                1 for i, q in enumerate(questions)
                if answers.get(str(i)) == q["correct"]
            )
            st.session_state["quiz_submitted"] = True
            st.session_state["quiz_score"] = score

            user_id = st.session_state.get("user_id")
            save_quiz_attempt(
                user_id,
                st.session_state.get("quiz_domain"),
                score,
                len(questions),
            )
            st.rerun()
    else:
        score = st.session_state.get("quiz_score", 0)
        total = len(questions)
        pct   = round(score / total * 100)
        if pct >= 75:
            st.balloons()
            st.success(f"🎉 Score: **{score}/{total} ({pct}%)** – Passing!")
        else:
            st.warning(f"Score: **{score}/{total} ({pct}%)** – Keep studying!")

        if st.button("Take Another Quiz", key="retake_quiz"):
            st.session_state.pop("quiz_questions", None)
            st.session_state.pop("quiz_submitted", None)
            st.rerun()
