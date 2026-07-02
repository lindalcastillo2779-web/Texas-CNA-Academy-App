"""Courses page for NATCEP-aligned study flow."""

from pathlib import Path

import streamlit as st

from utils.media import read_markdown_document, render_module_media, render_page_media

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
    render_page_media("courses")

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
    module_path = CURRICULUM_DIR / selected
    frontmatter, content, read_failed = read_markdown_document(module_path)

    if read_failed:
        st.error("Unable to read the selected module file. Please try another module.")
        return

    render_module_media(str(frontmatter.get("module_id") or module_path.stem), frontmatter)
    if not content:
        st.warning("The selected module file is currently empty.")
        return

    st.markdown(content)
    st.info("When you complete a module, use 📚 Exam Prep in the sidebar to quiz that topic.")


def _read_markdown(path: Path) -> tuple[str, bool]:
    _, content, read_failed = read_markdown_document(path)
    return content, read_failed


def _to_label(path: Path) -> str:
    frontmatter, content, _ = read_markdown_document(path)
    title = str(frontmatter.get("title") or "").strip()
    if title:
        return title
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return path.stem.replace("_", " ").replace("-", " ").title()
