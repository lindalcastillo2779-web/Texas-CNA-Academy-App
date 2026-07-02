"""
Buddy service – role-aware study and compliance assistant
=========================================================
Builds the system prompt, performs optional RAG retrieval,
calls the LLM via llm_client, and returns a grounded reply.
"""

from __future__ import annotations

import os
from typing import Optional

import llm_client
import knowledge_loader

# ─────────────────────────────────────────────────────────────────────────────
# Role-specific guidance injected into the system prompt
# ─────────────────────────────────────────────────────────────────────────────
_ROLE_GUIDANCE: dict[str, str] = {
    "Student": (
        "You are helping a nurse aide student studying for the Texas NATCEP "
        "certification exam. Use plain, encouraging language. Offer to quiz the "
        "student, give rationales for clinical skills steps, and celebrate correct "
        "answers. Break down complex topics into easy-to-remember bullet points."
    ),
    "Instructor": (
        "You are assisting a Texas CNA program instructor. Provide lesson-planning "
        "support, suggest quiz questions aligned to NATCEP domains, and help draft "
        "skills checklists. Reference the approved Texas curriculum where relevant."
    ),
    "DON": (
        "You are assisting a Director of Nursing (DON). Focus on compliance "
        "readiness, CNA renewal tracking, staffing ratios, and documentation "
        "requirements. Reference HHSC/HHS and TWC rules accurately."
    ),
    "Facility": (
        "You are assisting a healthcare facility administrator or compliance officer. "
        "Focus on nurse aide registry requirements, program approval, staffing "
        "compliance, and TULIP reporting. Provide actionable checklists."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# Core safety / grounding instructions (always included)
# ─────────────────────────────────────────────────────────────────────────────
_SAFETY_INSTRUCTIONS = """
IMPORTANT GUIDELINES YOU MUST FOLLOW:
- You are Buddy, an educational assistant for Texas CNA Academy (TULIP-Link).
- Only answer questions related to CNA curriculum, TULIP, TWC, Texas HHSC/HHS, or
  Texas nurse aide certification and renewal topics.
- NEVER fabricate specific laws, regulatory deadlines, form numbers, or agency rules.
- When you are uncertain, explicitly say so and recommend checking the official source.
- Always remind users that your answers are for EDUCATIONAL GUIDANCE ONLY —
  not legal or medical advice — and that official Texas agency sources should be
  verified for binding policy details.
- If the question is outside your scope, politely decline and explain what you can help with.
- Keep answers concise and actionable unless the user asks for more detail.
- Provide source attribution (file name or agency name) whenever you use retrieved context.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Lazy-loaded FAISS index (loaded once per process)
# ─────────────────────────────────────────────────────────────────────────────
_index  = None
_chunks: Optional[list] = None
_index_loaded = False


def _ensure_index() -> bool:
    """Load the FAISS index on first call; return True if index is available."""
    global _index, _chunks, _index_loaded
    if not _index_loaded:
        _index, _chunks = knowledge_loader.load_index()
        _index_loaded = True
    return _index is not None


def _build_system_prompt(role: str, context_snippets: list[dict]) -> str:
    role_text = _ROLE_GUIDANCE.get(role, _ROLE_GUIDANCE["Student"])

    context_section = ""
    if context_snippets:
        lines = []
        for snip in context_snippets:
            src = snip.get("source", "unknown")
            lines.append(f"[Source: {src}]\n{snip['text']}")
        context_section = (
            "\n\nRELEVANT KNOWLEDGE BASE CONTEXT (use this to ground your answer):\n"
            + "\n---\n".join(lines)
            + "\n"
        )

    return f"{_SAFETY_INSTRUCTIONS}\nROLE CONTEXT: {role_text}{context_section}"


def ask_buddy(
    question: str,
    role: str = "Student",
    history: Optional[list[dict]] = None,
    style: str = "concise",
) -> dict:
    """
    Main entry point for Buddy.

    Parameters
    ----------
    question : the user's latest message
    role     : one of Student | Instructor | DON | Facility
    history  : prior conversation turns as OpenAI message dicts
    style    : "concise" or "detailed"

    Returns
    -------
    dict with keys:
      "answer"        – the assistant's reply string
      "sources"       – list of source strings used in context
      "rag_used"      – bool, whether retrieved context was included
      "index_missing" – bool, True if no knowledge index exists
      "error"         – str or None
    """
    history = history or []

    # 1. RAG retrieval
    rag_used      = False
    index_missing = False
    snippets: list[dict] = []

    if _ensure_index():
        snippets  = knowledge_loader.retrieve(question, _index, _chunks, top_k=4)
        rag_used  = bool(snippets)
    else:
        index_missing = True

    # 2. Build system prompt
    system_prompt = _build_system_prompt(role, snippets)
    if style == "detailed":
        system_prompt += (
            "\n\nThe user has requested a DETAILED response. "
            "Expand your answer with thorough explanations, examples, and references."
        )

    # 3. Assemble messages
    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    # 4. Call LLM
    try:
        answer = llm_client.chat_completion(messages, temperature=0.3)
        sources = list({s["source"] for s in snippets}) if snippets else []
        return {
            "answer":        answer,
            "sources":       sources,
            "rag_used":      rag_used,
            "index_missing": index_missing,
            "error":         None,
        }
    except (ValueError, RuntimeError) as exc:
        return {
            "answer":        None,
            "sources":       [],
            "rag_used":      False,
            "index_missing": index_missing,
            "error":         str(exc),
        }
    except Exception as exc:
        # Catch remaining Exception subclasses (e.g. openai.APIError, network errors).
        # BaseException subclasses (KeyboardInterrupt, SystemExit) are intentionally
        # excluded so they propagate normally.
        return {
            "answer":        None,
            "sources":       [],
            "rag_used":      False,
            "index_missing": index_missing,
            "error":         f"Unexpected error: {exc}",
        }
