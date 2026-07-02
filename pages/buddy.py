"""Buddy – AI study and compliance chatbot page."""

import os

import streamlit as st

import buddy_service

ROLES   = ["Student", "Instructor", "DON", "Facility"]
STYLES  = ["concise", "detailed"]

# Role descriptions shown in the UI
_ROLE_DESCRIPTIONS = {
    "Student":    "Studying for NATCEP certification",
    "Instructor": "Curriculum and lesson-planning support",
    "DON":        "Compliance, renewal tracking, and staffing",
    "Facility":   "Registry, program approval, and TULIP reporting",
}


def show() -> None:
    st.title("🤖 Buddy – Your CNA Study & Compliance Assistant")
    st.caption(
        "Ask Buddy about the curriculum, TULIP, TWC, or Texas HHSC/HHS topics. "
        "Educational guidance only — always verify policy details with official sources."
    )

    # ── Sidebar controls ────────────────────────────────────────────────────
    with st.sidebar:
        st.divider()
        st.subheader("🤖 Buddy Settings")
        role = st.selectbox(
            "Your role",
            ROLES,
            format_func=lambda r: f"{r} — {_ROLE_DESCRIPTIONS[r]}",
            key="buddy_role",
        )
        style = st.selectbox(
            "Response style",
            STYLES,
            format_func=lambda s: s.capitalize(),
            key="buddy_style",
        )
        if st.button("🗑️ Clear chat", key="buddy_clear"):
            st.session_state["buddy_history"]  = []
            st.session_state["buddy_messages"] = []
            st.rerun()

    # ── Session state init ──────────────────────────────────────────────────
    if "buddy_messages" not in st.session_state:
        st.session_state["buddy_messages"] = []   # display messages
    if "buddy_history" not in st.session_state:
        st.session_state["buddy_history"] = []    # OpenAI message dicts

    # ── LLM / config status banner ──────────────────────────────────────────
    _show_config_status()

    # ── Chat history display ─────────────────────────────────────────────────
    for msg in st.session_state["buddy_messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📚 Sources used", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(f"- `{src}`")

    # ── User input ───────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask Buddy a question…")
    if not user_input:
        _show_suggested_questions(role)
        return

    # Append user message
    st.session_state["buddy_messages"].append({"role": "user", "content": user_input})
    st.session_state["buddy_history"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # ── Buddy response ───────────────────────────────────────────────────────
    with st.chat_message("assistant"):
        with st.spinner("Buddy is thinking…"):
            result = buddy_service.ask_buddy(
                question=user_input,
                role=role,
                history=st.session_state["buddy_history"][:-1],  # exclude latest user msg
                style=style,
            )

        if result["error"]:
            _render_error(result["error"])
            return

        answer = result["answer"] or ""
        st.markdown(answer)

        # Source attribution
        if result["sources"]:
            with st.expander("📚 Sources used", expanded=False):
                for src in result["sources"]:
                    st.markdown(f"- `{src}`")
        elif result["index_missing"]:
            st.caption(
                "ℹ️ No knowledge index found — answering from general training data. "
                "Run `python knowledge_loader.py` after adding docs to `knowledge/`."
            )

    # Persist assistant message
    st.session_state["buddy_messages"].append(
        {
            "role":    "assistant",
            "content": answer,
            "sources": result.get("sources", []),
        }
    )
    st.session_state["buddy_history"].append({"role": "assistant", "content": answer})


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _show_config_status() -> None:
    """Display a warning banner when LLM credentials are not configured."""
    provider = os.environ.get("LLM_PROVIDER", "OPENAI").upper()
    if provider == "AZURE_OPENAI":
        configured = bool(
            os.environ.get("AZURE_OPENAI_KEY") and
            os.environ.get("AZURE_OPENAI_ENDPOINT") and
            os.environ.get("AZURE_OPENAI_DEPLOYMENT")
        )
    else:
        configured = bool(os.environ.get("OPENAI_API_KEY"))

    if not configured:
        st.warning(
            "⚠️ **Buddy is not yet configured.** "
            "Set `OPENAI_API_KEY` (or Azure equivalents) in your `.env` file or "
            "Render environment variables, then restart the app. "
            "See the README for setup instructions.",
            icon="🔑",
        )


def _render_error(error_msg: str) -> None:
    if "API_KEY" in error_msg or "not set" in error_msg.lower():
        st.error(
            f"🔑 **Configuration error:** {error_msg}\n\n"
            "Add your API key to `.env` (see `.env.example`) and restart the app."
        )
    elif "not installed" in error_msg.lower():
        st.error(
            f"📦 **Missing package:** {error_msg}\n\n"
            "Run `pip install -r requirements.txt` and restart."
        )
    else:
        st.error(f"❌ **Buddy encountered an error:** {error_msg}")


def _show_suggested_questions(role: str) -> None:
    """Show starter prompts tailored to the selected role."""
    suggestions: dict[str, list[str]] = {
        "Student": [
            "What are the NATCEP exam domains I need to study?",
            "Explain the steps for hand hygiene.",
            "Quiz me on range-of-motion exercises.",
        ],
        "Instructor": [
            "What topics are required in the Texas CNA curriculum?",
            "Help me write quiz questions on infection control.",
            "What are the clinical skills hour requirements?",
        ],
        "DON": [
            "What are the CNA renewal requirements in Texas?",
            "How do I check a CNA's status on the nurse aide registry?",
            "What does TULIP require for program reporting?",
        ],
        "Facility": [
            "What are the HHSC requirements for CNA training programs?",
            "How do I apply for a NATCEP program approval?",
            "What TWC resources are available for workforce training?",
        ],
    }
    prompts = suggestions.get(role, suggestions["Student"])
    st.divider()
    st.markdown("**💡 Try asking Buddy:**")
    for prompt in prompts:
        st.markdown(f"- _{prompt}_")
