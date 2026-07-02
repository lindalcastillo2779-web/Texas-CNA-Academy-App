"""Courses page for NATCEP-aligned study flow."""

from pathlib import Path

import streamlit as st

CURRICULUM_DIR = Path(__file__).resolve().parents[1] / "knowledge" / "curriculum"

NATCEP_FLOW = [
    ("1", "Start with foundational modules", "Role, safety, and infection-control basics."),
    ("2", "Review each module checklist", "Use objectives and skill drills before quizzes."),
    ("3", "Take practice quizzes", "Move to Exam Prep after each module block."),
    ("4", "Track readiness", "Use CEU and Renewal sections as your progress grows."),
]


def show() -> None:
    st.title("🎓 Courses – NATCEP Study Path")
    st.caption("Browse curriculum modules first, then move to quizzes and readiness tools.")

    st.subheader("Texas CNA / NATCEP learning flow")
    cols = st.columns(len(NATCEP_FLOW))
    for col, (step, title, desc) in zip(cols, NATCEP_FLOW):
        with col:
            st.markdown(f"**Step {step}: {title}**")
            st.write(desc)

    st.divider()
    st.subheader("Course content library")

    course_files = sorted(CURRICULUM_DIR.rglob("*.md"))
    if not course_files:
        st.warning(
            "No curriculum markdown files were found in knowledge/curriculum. "
            "Add module files to expand the course library."
        )
        return

    module_paths = [f.relative_to(CURRICULUM_DIR).as_posix() for f in course_files]
    labels = {p: _to_label(CURRICULUM_DIR / p) for p in module_paths}
    selected = st.selectbox(
        "Choose a course module",
        module_paths,
        format_func=lambda p: labels.get(p, p),
    )
    content, read_failed = _read_markdown(CURRICULUM_DIR / selected)

    if read_failed:
        st.error("Unable to read the selected module file. Please try another module.")
        return
    if not content:
        st.warning("The selected module file is currently empty.")
        return

    st.markdown(content)
    st.info("When you complete a module, use 📚 Exam Prep in the sidebar to quiz that topic.")


def _read_markdown(path: Path) -> tuple[str, bool]:
    try:
        return path.read_text(encoding="utf-8").strip(), False
    except (OSError, UnicodeError):
        return "", True


def _to_label(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as file_obj:
            first_line = file_obj.readline().strip()
    except (OSError, UnicodeError):
        first_line = ""
    if first_line.startswith("#"):
        return first_line.lstrip("#").strip()
    return path.stem.replace("_", " ").replace("-", " ").title()
