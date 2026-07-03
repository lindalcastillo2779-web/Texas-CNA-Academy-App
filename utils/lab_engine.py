"""Clinical Skills Lab engine – scenario loading, step progression, scoring, and feedback.

This module is intentionally dependency-free beyond the Python standard library so it can
be used from any Streamlit page without additional requirements.
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
    """Return a list of available scenarios as ``{"id": ..., "title": ..., "description": ...}``."""
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
# Session-state initialiser
# ---------------------------------------------------------------------------

def init_lab_session(state: Any, scenario_id: str, mode: str) -> None:
    """Initialise Streamlit session state keys for a new lab run.

    Parameters
    ----------
    state:
        ``st.session_state`` (or any dict-like object for testing).
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
    state["lab_step_index"] = 0
    # Dict of step_id → chosen option id (str)
    state["lab_step_answers"] = {}
    # Dict of comm_id → chosen option id (str)
    state["lab_comm_answers"] = {}
    state["lab_complete"] = False
    state["lab_total_steps"] = len(steps)
    state["lab_total_comms"] = len(comms)


def reset_lab_session(state: Any) -> None:
    """Remove all lab-related keys from session state."""
    keys = [k for k in dir(state) if k.startswith("lab_")]
    for k in keys:
        try:
            del state[k]
        except (KeyError, AttributeError):
            pass


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
      - ``critical`` (bool)  – mirrors the step's criticality flag
      - ``feedback`` (str)   – shown immediately in Coach mode, deferred in Exam mode
      - ``rationale`` (str | None) – shown in Coach mode for wrong answers
    """
    dps = step.get("decision_points", [])
    if dp_index >= len(dps):
        return {"correct": False, "critical": step.get("critical", False), "feedback": "", "rationale": None}

    dp = dps[dp_index]
    correct_id = dp.get("correct_option")
    is_critical = step.get("critical", False)

    chosen_opt = next((o for o in dp.get("options", []) if o["id"] == chosen_option_id), None)
    if chosen_opt is None:
        return {"correct": False, "critical": is_critical, "feedback": "Invalid selection.", "rationale": None}

    is_correct = chosen_opt.get("correct", False)
    feedback = chosen_opt.get("feedback", "")
    rationale = chosen_opt.get("rationale")

    # In Exam mode, suppress immediate rationale feedback for wrong answers
    if mode == "exam" and not is_correct:
        feedback = "❌ Incorrect selection recorded."
        rationale = None

    return {
        "correct": is_correct,
        "critical": is_critical,
        "feedback": feedback,
        "rationale": rationale,
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
    else:
        if mode == "exam":
            feedback = "❌ Communication checkpoint not met."
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
      - ``checklist_score`` (int)  – correct non-critical steps (0–100)
      - ``critical_step_score`` (int)  – critical steps all correct = 100, else 0
      - ``communication_score`` (int)  – communication checkpoints (0–100)
      - ``overall_score`` (int)  – weighted composite (0–100)
      - ``pass_ready`` (bool)  – True if all critical steps correct AND overall ≥ pass threshold
      - ``critical_misses`` (list[dict])  – steps that were critical and answered incorrectly
      - ``step_results`` (list[dict])  – per-step pass/fail breakdown
      - ``remediation_targets`` (list[dict])  – targeted remediation suggestions
    """
    mapping = load_curriculum_mapping()
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

    step_results = []
    critical_misses = []
    remediation_targets = []

    # --- Step scoring ---
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

        # For simplicity each step has one primary decision point
        dp = dps[0]
        correct_opt_id = dp.get("correct_option")
        chosen = step_answers.get(step_id)
        is_correct = chosen == correct_opt_id

        step_map = scenario_step_mapping.get(step_id, {})
        step_result = {
            "step_id": step_id,
            "title": step.get("title", step_id),
            "critical": is_critical,
            "correct": is_correct,
            "chosen": chosen,
            "correct_option": correct_opt_id,
            "domain": step_map.get("domain", ""),
            "curriculum_module": step_map.get("curriculum_module", ""),
            "curriculum_topic": step_map.get("curriculum_topic", ""),
            "remediation_ref": dp.get("remediation_ref"),
        }
        step_results.append(step_result)

        if is_critical:
            critical_total += 1
            if is_correct:
                critical_correct += 1
            else:
                critical_misses.append(step_result)
                # Build remediation entry
                ref_key = dp.get("remediation_ref")
                ref_info = scenario.get("remediation_refs", {}).get(ref_key, {})
                remediation_targets.append({
                    "step_title": step.get("title", step_id),
                    "module": ref_info.get("module", step_map.get("curriculum_module", "")),
                    "topic": ref_info.get("topic", step_map.get("curriculum_topic", "")),
                    "exam_domain": ref_info.get("exam_domain", step_map.get("domain", "")),
                    "prometric_skill": ref_info.get("prometric_skill", ""),
                    "label": ref_info.get("label", ""),
                })
        else:
            non_critical_total += 1
            if is_correct:
                non_critical_correct += 1
            elif chosen is not None and not is_correct:
                ref_key = dp.get("remediation_ref")
                ref_info = scenario.get("remediation_refs", {}).get(ref_key, {})
                remediation_targets.append({
                    "step_title": step.get("title", step_id),
                    "module": ref_info.get("module", step_map.get("curriculum_module", "")),
                    "topic": ref_info.get("topic", step_map.get("curriculum_topic", "")),
                    "exam_domain": ref_info.get("exam_domain", step_map.get("domain", "")),
                    "prometric_skill": ref_info.get("prometric_skill", ""),
                    "label": ref_info.get("label", ""),
                })

    checklist_score = (
        round(non_critical_correct / non_critical_total * 100) if non_critical_total > 0 else 100
    )

    # Critical step score: all-or-nothing per critical step
    critical_step_score = (
        round(critical_correct / critical_total * 100) if critical_total > 0 else 100
    )

    # --- Communication scoring ---
    comm_points_earned = 0
    comm_points_total = 0
    for comm in comms:
        comm_id = comm.get("id")
        points = comm.get("points", 5)
        comm_points_total += points
        chosen = comm_answers.get(comm_id)
        correct_opt_id = comm.get("correct_option")
        if chosen == correct_opt_id:
            comm_points_earned += points

    communication_score = (
        round(comm_points_earned / comm_points_total * 100) if comm_points_total > 0 else 100
    )

    # --- Weighted composite ---
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

    # Deduplicate remediation targets by topic
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
    """Return a list of prioritised next-step recommendation strings."""
    recommendations: list[str] = []

    if not scores.get("all_criticals_passed"):
        recommendations.append(
            "🚨 **Critical step(s) missed.** Review infection control, safety, and exam-critical "
            "technique steps immediately — these cause automatic failure on the Prometric exam."
        )
    if scores.get("critical_step_score", 100) < 100:
        for miss in scores.get("critical_misses", []):
            mod = miss.get("curriculum_module", "")
            topic = miss.get("curriculum_topic", "")
            if mod or topic:
                recommendations.append(f"📌 Re-study: **{mod} – {topic}**")

    if scores.get("checklist_score", 100) < 80:
        recommendations.append(
            "📋 **Checklist completion below 80%.** Practice each skill step in sequence before "
            "attempting Exam Mode."
        )

    if scores.get("communication_score", 100) < 80:
        recommendations.append(
            "💬 **Communication score below 80%.** Practice greeting, explaining procedures, and "
            "ensuring resident comfort — these are scored on the CNA exam."
        )

    if scores.get("pass_ready"):
        recommendations.append(
            "✅ **You are showing exam readiness for this skill.** Continue practicing in Exam Mode "
            "and expand to other lab scenarios."
        )
    else:
        recommendations.append(
            "📚 **Use Coach Mode** to review rationale for each incorrect answer, then retry in Exam Mode."
        )

    # Targeted remediation
    for r in scores.get("remediation_targets", [])[:3]:
        label = r.get("label") or r.get("topic", "")
        module = r.get("module", "")
        if label and module:
            recommendations.append(f"📖 Targeted review: **{module}** → {label}")

    return recommendations
