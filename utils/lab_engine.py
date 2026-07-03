"""Clinical Skills Lab engine – scenario loading, step progression, scoring, and feedback.

Aligned to:
- Texas HHSC NATCEP Curriculum Standards (2024)
- Prometric CNA Skills Evaluation Checklist (Texas pool)
- Texas Administrative Code Title 26, Chapter 95 (NATCEP)
- TULIP (Texas Unified Licensure Information Portal) reporting standards

This module is intentionally dependency-free beyond the Python standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCENARIOS_DIR = _REPO_ROOT / "knowledge" / "lab_scenarios"
_CURRICULUM_MAPPING_PATH = _SCENARIOS_DIR / "curriculum_mapping.json"

# Scenario file registry – maps scenario_id → JSON filename
_SCENARIO_FILES: dict[str, str] = {
    "hand_hygiene_ppe": "hand_hygiene_ppe.json",
    "transfer_bed_wheelchair": "transfer_bed_wheelchair.json",
    "vital_signs_documentation": "vital_signs_documentation.json",
}

# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


def list_scenarios() -> list[dict[str, str]]:
    """Return a list of available scenarios as summary dicts."""
    scenarios = []
    for sid, fname in _SCENARIO_FILES.items():
        path = _SCENARIOS_DIR / fname
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            scenarios.append({
                "id": sid,
                "title": data.get("title", sid),
                "description": data.get("description", ""),
                "natcep_domains": data.get("natcep_domains", []),
                "estimated_minutes": data.get("estimated_minutes", 0),
                "prometric_skill": data.get("texas_2024_alignment", {}).get("prometric_skill_title", ""),
            })
        except (OSError, json.JSONDecodeError):
            pass
    return scenarios


def load_scenario(scenario_id: str) -> dict[str, Any]:
    """Load and return a scenario definition dict, or ``{}`` if not found."""
    fname = _SCENARIO_FILES.get(scenario_id)
    if fname is None:
        return {}
    path = _SCENARIOS_DIR / fname
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_curriculum_mapping() -> dict[str, Any]:
    """Load and return the curriculum_mapping.json dict."""
    try:
        return json.loads(_CURRICULUM_MAPPING_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


# ---------------------------------------------------------------------------
# Pre-simulation knowledge check helpers
# ---------------------------------------------------------------------------


def has_pre_knowledge_check(scenario: dict[str, Any]) -> bool:
    """Return True if the scenario has pre-simulation knowledge-check questions."""
    return bool(scenario.get("pre_simulation_knowledge_check"))


def get_pre_check_questions(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the list of pre-simulation knowledge-check question dicts."""
    return scenario.get("pre_simulation_knowledge_check", [])


def evaluate_pre_check_answer(
    question: dict[str, Any],
    chosen_option_id: str,
) -> dict[str, Any]:
    """Evaluate a single pre-check question.

    Returns a result dict with: correct (bool), feedback (str), explanation (str).
    """
    correct_id = question.get("correct_option")
    is_correct = chosen_option_id == correct_id
    options = question.get("options", [])
    chosen_opt = next((o for o in options if o["id"] == chosen_option_id), None)
    correct_opt = next((o for o in options if o["id"] == correct_id), None)
    feedback = question.get("explanation", "")
    return {
        "correct": is_correct,
        "chosen_text": chosen_opt.get("text", "") if chosen_opt else "",
        "correct_text": correct_opt.get("text", "") if correct_opt else "",
        "explanation": feedback,
        "texas_standard": question.get("texas_standard", ""),
    }


def compute_pre_check_score(
    questions: list[dict[str, Any]],
    answers: dict[str, str],
) -> dict[str, Any]:
    """Compute the pre-check score."""
    total = len(questions)
    correct = sum(
        1 for q in questions
        if answers.get(q["id"]) == q.get("correct_option")
    )
    return {
        "total": total,
        "correct": correct,
        "pct": round(correct / total * 100) if total else 0,
    }


# ---------------------------------------------------------------------------
# Session-state initialiser
# ---------------------------------------------------------------------------


def init_lab_session(state: Any, scenario_id: str, mode: str) -> None:
    """Initialise Streamlit session state keys for a new lab run.

    Parameters
    ----------
    state:
        ``st.session_state`` (or any dict-like for testing).
    scenario_id:
        One of the keys in ``_SCENARIO_FILES``.
    mode:
        ``"coach"`` or ``"exam"``.
    """
    scenario = load_scenario(scenario_id)
    steps = scenario.get("steps", [])
    comms = scenario.get("communication_checkpoints", [])

    state["lab_scenario_id"] = scenario_id
    state["lab_scenario"] = scenario
    state["lab_mode"] = mode
    # phase: "briefing" | "pre_check" | "simulation" | "complete"
    state["lab_phase"] = "briefing"
    state["lab_step_index"] = 0
    state["lab_step_answers"] = {}
    state["lab_comm_answers"] = {}
    state["lab_complete"] = False
    state["lab_total_steps"] = len(steps)
    state["lab_total_comms"] = len(comms)
    # Pre-check state
    state["lab_pre_check_index"] = 0
    state["lab_pre_check_answers"] = {}
    state["lab_pre_check_score"] = None
    # Feedback shown for current step (cleared on advance)
    state["lab_step_feedback"] = None


def reset_lab_session(state: Any) -> None:
    """Remove all lab-related keys from session state."""
    keys_to_remove = [k for k in list(state.keys()) if k.startswith("lab_")]
    for k in keys_to_remove:
        del state[k]


# ---------------------------------------------------------------------------
# Step evaluation
# ---------------------------------------------------------------------------


def evaluate_step_answer(
    step: dict[str, Any],
    dp_index: int,
    chosen_option_id: str,
    mode: str,
) -> dict[str, Any]:
    """Evaluate a single decision point answer.

    Returns a result dict with keys:
      - ``correct`` (bool)
      - ``critical`` (bool)
      - ``feedback`` (str)   – immediate in Coach; suppressed in Exam
      - ``rationale`` (str | None)
      - ``exam_tip`` (str | None)
      - ``consequence`` (str | None)  – clinical consequence of wrong answer
      - ``remediation_ref`` (str | None)
    """
    dps = step.get("decision_points", [])
    if dp_index >= len(dps):
        return {"correct": False, "critical": step.get("critical", False), "feedback": "", "rationale": None}

    dp = dps[dp_index]
    is_critical = step.get("critical", False)
    chosen_opt = next((o for o in dp.get("options", []) if o["id"] == chosen_option_id), None)
    if chosen_opt is None:
        return {"correct": False, "critical": is_critical, "feedback": "Invalid selection.", "rationale": None}

    is_correct = chosen_opt.get("correct", False)
    feedback = chosen_opt.get("feedback", "")
    rationale = chosen_opt.get("rationale")
    consequence = chosen_opt.get("consequence")

    if mode == "exam" and not is_correct:
        feedback = "❌ Answer recorded. Full feedback will appear in your results summary."
        rationale = None
        consequence = None

    return {
        "correct": is_correct,
        "critical": is_critical,
        "feedback": feedback,
        "rationale": rationale,
        "consequence": consequence,
        "exam_tip": step.get("exam_tip"),
        "remediation_ref": dp.get("remediation_ref"),
    }


def evaluate_comm_answer(
    comm: dict[str, Any],
    chosen_option_id: str,
    mode: str,
) -> dict[str, Any]:
    """Evaluate a communication checkpoint answer."""
    correct_id = comm.get("correct_option")
    is_correct = chosen_option_id == correct_id
    points = comm.get("points", 5)

    if is_correct:
        feedback = comm.get("feedback_pass", "✅ Communication step completed.")
    elif mode == "exam":
        feedback = "❌ Communication checkpoint not met. Details in final summary."
    else:
        feedback = comm.get("feedback_fail", "❌ Communication step missed.")

    return {
        "correct": is_correct,
        "points": points if is_correct else 0,
        "feedback": feedback,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def compute_scores(
    scenario: dict[str, Any],
    step_answers: dict[str, str],
    comm_answers: dict[str, str],
    curriculum_mapping: dict[str, Any],
) -> dict[str, Any]:
    """Compute the full scoring breakdown for a completed lab run.

    Returns a dict with:
      - ``checklist_score`` (int 0–100)
      - ``critical_step_score`` (int 0–100)
      - ``communication_score`` (int 0–100)
      - ``overall_score`` (int 0–100)
      - ``pass_ready`` (bool)
      - ``critical_misses`` (list[dict])
      - ``step_results`` (list[dict])
      - ``remediation_targets`` (list[dict])
    """
    mapping = curriculum_mapping or load_curriculum_mapping()
    weights = mapping.get("scoring_weights", {
        "checklist_score_weight": 0.40,
        "critical_step_score_weight": 0.40,
        "communication_score_weight": 0.20,
    })
    pass_thresholds = mapping.get("pass_thresholds", {
        "overall_pass_pct": 75,
        "critical_steps_pass_pct": 100,
    })

    steps = scenario.get("steps", [])
    comms = scenario.get("communication_checkpoints", [])
    scenario_id = scenario.get("id", "")
    scenario_step_mapping = (
        mapping.get("scenario_mappings", {})
        .get(scenario_id, {})
        .get("steps", {})
    )

    step_results: list[dict] = []
    critical_misses: list[dict] = []
    remediation_targets: list[dict] = []

    critical_total = 0
    critical_correct = 0
    non_critical_total = 0
    non_critical_correct = 0

    for step in steps:
        step_id = step.get("id")
        is_critical = step.get("critical", False)
        dps = step.get("decision_points", [])
        if not dps:
            continue
        dp = dps[0]
        correct_opt_id = dp.get("correct_option")
        chosen = step_answers.get(step_id)
        is_correct = chosen == correct_opt_id
        step_map = scenario_step_mapping.get(step_id, {})

        step_result: dict[str, Any] = {
            "step_id": step_id,
            "title": step.get("title", step_id),
            "critical": is_critical,
            "correct": is_correct,
            "chosen": chosen,
            "correct_option": correct_opt_id,
            "domain": step_map.get("domain", ""),
            "curriculum_module": step_map.get("curriculum_module", ""),
            "curriculum_topic": step_map.get("curriculum_topic", ""),
            "exam_notes": step_map.get("exam_notes", ""),
            "remediation_ref": dp.get("remediation_ref"),
        }
        step_results.append(step_result)

        ref_key = dp.get("remediation_ref")
        ref_info = scenario.get("remediation_refs", {}).get(ref_key, {})

        if is_critical:
            critical_total += 1
            if is_correct:
                critical_correct += 1
            else:
                critical_misses.append(step_result)
                remediation_targets.append({
                    "step_title": step.get("title", step_id),
                    "module": ref_info.get("module", step_map.get("curriculum_module", "")),
                    "topic": ref_info.get("topic", step_map.get("curriculum_topic", "")),
                    "exam_domain": ref_info.get("exam_domain", step_map.get("domain", "")),
                    "prometric_skill": ref_info.get("prometric_skill", ""),
                    "label": ref_info.get("label", ""),
                    "critical": True,
                })
        else:
            non_critical_total += 1
            if is_correct:
                non_critical_correct += 1
            elif chosen is not None:
                remediation_targets.append({
                    "step_title": step.get("title", step_id),
                    "module": ref_info.get("module", step_map.get("curriculum_module", "")),
                    "topic": ref_info.get("topic", step_map.get("curriculum_topic", "")),
                    "exam_domain": ref_info.get("exam_domain", step_map.get("domain", "")),
                    "prometric_skill": ref_info.get("prometric_skill", ""),
                    "label": ref_info.get("label", ""),
                    "critical": False,
                })

    checklist_score = (
        round(non_critical_correct / non_critical_total * 100) if non_critical_total > 0 else 100
    )
    critical_step_score = (
        round(critical_correct / critical_total * 100) if critical_total > 0 else 100
    )

    comm_points_earned = 0
    comm_points_total = 0
    for comm in comms:
        comm_id = comm.get("id")
        points = comm.get("points", 5)
        comm_points_total += points
        if comm_answers.get(comm_id) == comm.get("correct_option"):
            comm_points_earned += points

    communication_score = (
        round(comm_points_earned / comm_points_total * 100) if comm_points_total > 0 else 100
    )

    w_check = weights.get("checklist_score_weight", 0.40)
    w_crit = weights.get("critical_step_score_weight", 0.40)
    w_comm = weights.get("communication_score_weight", 0.20)
    overall_score = round(
        checklist_score * w_check
        + critical_step_score * w_crit
        + communication_score * w_comm
    )

    pass_threshold = pass_thresholds.get("overall_pass_pct", 75)
    all_criticals_passed = critical_total == 0 or critical_correct == critical_total
    pass_ready = all_criticals_passed and overall_score >= pass_threshold

    # Deduplicate by topic
    seen_topics: set[str] = set()
    unique_remediation: list[dict] = []
    for r in remediation_targets:
        key = r.get("topic", "") or r.get("module", "")
        if key not in seen_topics:
            seen_topics.add(key)
            unique_remediation.append(r)

    return {
        "checklist_score": checklist_score,
        "critical_step_score": critical_step_score,
        "communication_score": communication_score,
        "overall_score": overall_score,
        "pass_ready": pass_ready,
        "all_criticals_passed": all_criticals_passed,
        "critical_total": critical_total,
        "critical_correct": critical_correct,
        "non_critical_total": non_critical_total,
        "non_critical_correct": non_critical_correct,
        "comm_points_earned": comm_points_earned,
        "comm_points_total": comm_points_total,
        "critical_misses": critical_misses,
        "step_results": step_results,
        "remediation_targets": unique_remediation,
        "pass_threshold": pass_threshold,
    }


def build_next_steps_text(scores: dict[str, Any], mode: str) -> list[str]:
    """Return a prioritised list of next-step recommendation strings."""
    recs: list[str] = []

    if not scores.get("all_criticals_passed"):
        recs.append(
            "🚨 **Critical step(s) missed** — these trigger automatic failure on the Prometric exam. "
            "Review the steps below and retry in Coach Mode before testing yourself in Exam Mode."
        )
    for miss in scores.get("critical_misses", []):
        mod = miss.get("curriculum_module", "")
        topic = miss.get("curriculum_topic", "")
        if mod or topic:
            recs.append(f"📌 Re-study: **{mod}** → {topic}")

    if scores.get("checklist_score", 100) < 80:
        recs.append(
            "📋 **Checklist completion below 80%.** Practice each skill step in sequence "
            "using Coach Mode before switching to Exam Mode."
        )

    if scores.get("communication_score", 100) < 80:
        recs.append(
            "💬 **Communication score below 80%.** The CNA exam scores resident greeting, "
            "procedure explanation, and post-care comfort check. Practice these with every simulation."
        )

    if scores.get("pass_ready"):
        recs.append(
            "✅ **Exam ready for this skill.** Continue in Exam Mode and expand to other scenarios."
        )
    else:
        recs.append(
            "📚 Use **Coach Mode** to review the full rationale for each incorrect answer, "
            "then test yourself in **Exam Mode** to simulate Prometric conditions."
        )

    for r in scores.get("remediation_targets", [])[:3]:
        label = r.get("label") or r.get("topic", "")
        module = r.get("module", "")
        if label and module:
            recs.append(f"📖 Targeted review: **{module}** → {label}")

    return recs
