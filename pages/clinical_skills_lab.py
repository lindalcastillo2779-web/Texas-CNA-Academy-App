"""Clinical Skills Lab – interactive CNA skill simulations aligned to Prometric/Pearson exam standards."""

from __future__ import annotations

import streamlit as st

from utils.lab_engine import (
    build_next_steps_text,
    compute_scores,
    evaluate_comm_answer,
    evaluate_step_answer,
    init_lab_session,
    list_scenarios,
    load_curriculum_mapping,
    load_scenario,
    reset_lab_session,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODE_COACH = "coach"
MODE_EXAM = "exam"

MODE_LABELS = {
    MODE_COACH: "🏋️ Coach Mode",
    MODE_EXAM: "🎓 Exam Mode",
}

MODE_DESCRIPTIONS = {
    MODE_COACH: (
        "**Coach Mode** provides hints, immediate feedback after each step, and full rationale "
        "for incorrect answers. Use this mode to learn the skill and understand *why* each step matters."
    ),
    MODE_EXAM: (
        "**Exam Mode** mirrors the Prometric skills exam format: limited hints, no rationale during the "
        "attempt, and strict scoring. Feedback and remediation are shown only in the final summary. "
        "Use this mode when you feel ready to test yourself."
    ),
}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def show() -> None:
    st.title("🧪 Clinical Skills Lab")
    st.caption("Prometric & NATCEP-aligned interactive skill simulations for CNA exam preparation")

    _render_intro()

    # Session state namespace guard
    if "lab_complete" not in st.session_state:
        st.session_state["lab_complete"] = False

    # If a simulation is active, route to the runner or results view
    if st.session_state.get("lab_scenario_id") and not _is_at_start():
        if st.session_state.get("lab_complete"):
            _render_results()
        else:
            _render_simulation()
        return

    # Otherwise show the selection screen
    _render_selection_screen()


# ---------------------------------------------------------------------------
# Intro / overview
# ---------------------------------------------------------------------------

def _render_intro() -> None:
    with st.expander("ℹ️ How to use the Clinical Skills Lab", expanded=False):
        st.markdown(
            """
### What is the Clinical Skills Lab?

The Clinical Skills Lab gives you **interactive, step-by-step simulations** of the hands-on skills
evaluated on the **Prometric CNA skills examination** (required by Texas HHSC/NATCEP). Each
scenario walks you through a skill using the same checklist format examiners use.

### Practice modes

| Mode | Hints | Feedback timing | Best used for |
|------|-------|-----------------|---------------|
| 🏋️ **Coach Mode** | ✅ Full hints and rationale | Immediate after each step | First-time practice, understanding why each step matters |
| 🎓 **Exam Mode** | ❌ Limited — mirrors real exam | Summary only after completion | Self-assessment, exam readiness check |

### Scoring breakdown

| Component | Weight | What it measures |
|-----------|--------|-----------------|
| ✅ Checklist score | 40 % | Correct technique steps (non-critical) |
| 🚨 Critical-step score | 40 % | Critical safety/infection-control steps — **any miss = major exam deduction** |
| 💬 Communication score | 20 % | Resident communication and professionalism checkpoints |

**Pass threshold:** 75 % overall AND 100 % on all critical steps.

### Available scenarios

- 🧼 **Hand Hygiene & PPE** – Hand-washing technique, donning/doffing sequence, post-care hygiene
- 🦽 **Transfer: Bed ↔ Wheelchair** – Environment prep, gait belt, brakes/footrests, body mechanics
- 🩺 **Vital Signs & Documentation** – Temp, pulse, respirations, BP, normal ranges, reporting

### Adding new scenarios

Place a new JSON file under `knowledge/lab_scenarios/` following the existing scenario structure,
then register it in `utils/lab_engine.py` in the `_SCENARIO_FILES` dictionary. Update
`knowledge/lab_scenarios/curriculum_mapping.json` with the step mappings for the new scenario.
            """
        )
    st.divider()


# ---------------------------------------------------------------------------
# Scenario / mode selection
# ---------------------------------------------------------------------------

def _render_selection_screen() -> None:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Select a scenario")
        scenarios = list_scenarios()
        if not scenarios:
            st.error("No scenarios found. Check that `knowledge/lab_scenarios/` contains valid JSON files.")
            return

        scenario_options = {s["title"]: s["id"] for s in scenarios}
        selected_title = st.radio(
            "Available scenarios",
            options=list(scenario_options.keys()),
            label_visibility="collapsed",
        )
        selected_id = scenario_options[selected_title]

        # Show scenario details
        selected = next((s for s in scenarios if s["id"] == selected_id), {})
        if selected:
            st.markdown(f"_{selected.get('description', '')}_")
            domains = selected.get("natcep_domains", [])
            if domains:
                st.markdown("**NATCEP Domains:** " + " · ".join(domains))
            mins = selected.get("estimated_minutes", 0)
            if mins:
                st.caption(f"⏱ Estimated time: {mins} minutes")

    with col_right:
        st.subheader("Select mode")
        mode_label = st.radio(
            "Practice mode",
            options=list(MODE_LABELS.values()),
            label_visibility="collapsed",
        )
        mode = MODE_COACH if MODE_LABELS[MODE_COACH] in mode_label else MODE_EXAM
        st.markdown(MODE_DESCRIPTIONS[mode])

    st.divider()
    if st.button("▶️ Start Simulation", type="primary", use_container_width=True):
        init_lab_session(st.session_state, selected_id, mode)
        st.rerun()


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------

def _render_simulation() -> None:
    scenario = st.session_state.get("lab_scenario", {})
    mode = st.session_state.get("lab_mode", MODE_COACH)
    step_index = st.session_state.get("lab_step_index", 0)
    steps = scenario.get("steps", [])
    comms = scenario.get("communication_checkpoints", [])
    total_steps = len(steps)
    total_comms = len(comms)

    # --- Header ---
    st.subheader(f"{scenario.get('title', 'Scenario')}")
    st.caption(f"{MODE_LABELS[mode]}  |  Step {min(step_index + 1, total_steps + total_comms)} of {total_steps + total_comms}")
    _render_progress_bar(step_index, total_steps + total_comms)

    if st.button("⛔ Abandon simulation", key="abandon_sim"):
        reset_lab_session(st.session_state)
        st.rerun()

    st.divider()

    # Phase A: skill steps
    if step_index < total_steps:
        _render_step(steps[step_index], step_index, mode)
        return

    # Phase B: communication checkpoints
    comm_index = step_index - total_steps
    if comm_index < total_comms:
        _render_comm_checkpoint(comms[comm_index], comm_index, mode)
        return

    # All done — compute scores and mark complete
    _finalise(scenario, mode)


def _render_progress_bar(current: int, total: int) -> None:
    if total > 0:
        pct = min(current / total, 1.0)
        st.progress(pct, text=f"Progress: {current}/{total} completed")


def _render_step(step: dict, step_index: int, mode: str) -> None:
    step_id = step.get("id")
    is_critical = step.get("critical", False)
    dps = step.get("decision_points", [])
    if not dps:
        _advance_step()
        return

    dp = dps[0]  # one primary decision point per step

    # Critical badge
    if is_critical:
        st.markdown("🚨 **Critical Step** – this step is auto-failed on the Prometric exam if missed")
    else:
        st.markdown("📋 **Skill Step**")

    st.markdown(f"### Step {step_index + 1}: {step.get('title', '')}")
    st.markdown(step.get("instruction", ""))

    # Coach mode hint
    if mode == MODE_COACH:
        st.info("💡 **Coach hint:** Read each option carefully and select the one that matches CNA exam standards.")

    options = dp.get("options", [])
    option_map = {o["id"]: o["text"] for o in options}
    option_ids = [o["id"] for o in options]
    option_labels = [f"{o['id']}) {o['text']}" for o in options]

    chosen_key = f"lab_choice_{step_id}"
    chosen_label = st.radio(
        dp.get("question", "Select the best answer:"),
        options=option_labels,
        key=chosen_key,
        label_visibility="visible",
    )
    chosen_id = chosen_label.split(")")[0].strip()

    if st.button("✔️ Submit Answer", key=f"submit_{step_id}", type="primary"):
        result = evaluate_step_answer(step, 0, chosen_id, mode)
        st.session_state["lab_step_answers"][step_id] = chosen_id

        if result["correct"]:
            st.success(result["feedback"])
        else:
            st.error(result["feedback"])
            if mode == MODE_COACH and result.get("rationale"):
                st.markdown(f"> **Exam rationale:** {result['rationale']}")

        # Advance after showing feedback
        st.session_state["lab_step_index"] += 1
        if mode == MODE_COACH:
            st.info("Click **Next Step** to continue.")
            if st.button("Next Step →", key=f"next_{step_id}"):
                st.rerun()
        else:
            st.rerun()


def _render_comm_checkpoint(comm: dict, comm_index: int, mode: str) -> None:
    comm_id = comm.get("id")
    total_steps = st.session_state.get("lab_total_steps", 0)
    step_display = total_steps + comm_index + 1

    st.markdown("💬 **Communication & Professionalism Checkpoint**")
    st.markdown(f"### Checkpoint {comm_index + 1}: {comm.get('prompt', '')}")

    options = comm.get("options", [])
    option_labels = [f"{o['id']}) {o['text']}" for o in options]

    chosen_label = st.radio(
        "Select your answer:",
        options=option_labels,
        key=f"lab_comm_{comm_id}",
        label_visibility="collapsed",
    )
    chosen_id = chosen_label.split(")")[0].strip()

    if st.button("✔️ Submit", key=f"submit_comm_{comm_id}", type="primary"):
        result = evaluate_comm_answer(comm, chosen_id, mode)
        st.session_state["lab_comm_answers"][comm_id] = chosen_id

        if result["correct"]:
            st.success(result["feedback"])
        else:
            st.warning(result["feedback"])

        st.session_state["lab_step_index"] += 1
        st.rerun()


def _advance_step() -> None:
    st.session_state["lab_step_index"] = st.session_state.get("lab_step_index", 0) + 1
    st.rerun()


def _finalise(scenario: dict, mode: str) -> None:
    mapping = load_curriculum_mapping()
    scores = compute_scores(
        scenario,
        st.session_state.get("lab_step_answers", {}),
        st.session_state.get("lab_comm_answers", {}),
        mapping,
    )
    st.session_state["lab_scores"] = scores
    st.session_state["lab_complete"] = True
    st.rerun()


# ---------------------------------------------------------------------------
# Results view
# ---------------------------------------------------------------------------

def _render_results() -> None:
    scenario = st.session_state.get("lab_scenario", {})
    mode = st.session_state.get("lab_mode", MODE_COACH)
    scores = st.session_state.get("lab_scores", {})

    st.subheader(f"📊 Results: {scenario.get('title', 'Scenario')}")
    st.caption(f"{MODE_LABELS[mode]}")

    # Pass/fail banner
    if scores.get("pass_ready"):
        st.success("🎉 **Exam Ready** – You met the passing threshold for this skill!")
    else:
        if not scores.get("all_criticals_passed"):
            st.error(
                "🚨 **Critical Step Failure** – One or more critical steps were missed. "
                "This would result in automatic skill failure on the Prometric exam."
            )
        else:
            st.warning(
                f"📋 Overall score below passing threshold ({scores.get('pass_threshold', 75)}%). "
                "Review the remediation guidance below and retry."
            )

    st.divider()

    # Score breakdown
    st.markdown("### Score Breakdown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "✅ Checklist Score",
        f"{scores.get('checklist_score', 0)}%",
        help="Correct non-critical technique steps. Weight: 40%",
    )
    c2.metric(
        "🚨 Critical Steps",
        f"{scores.get('critical_step_score', 0)}%",
        help="Critical steps completed correctly. Weight: 40%. Must be 100% to pass.",
    )
    c3.metric(
        "💬 Communication",
        f"{scores.get('communication_score', 0)}%",
        help="Communication and professionalism checkpoints. Weight: 20%",
    )
    c4.metric(
        "🎯 Overall Score",
        f"{scores.get('overall_score', 0)}%",
        help=f"Weighted composite. Pass threshold: {scores.get('pass_threshold', 75)}%",
    )

    st.divider()

    # Step-by-step breakdown
    st.markdown("### Step Review")
    for sr in scores.get("step_results", []):
        icon = "✅" if sr["correct"] else ("🚨" if sr["critical"] else "❌")
        label = f"{icon} **{sr['title']}**"
        if sr["critical"]:
            label += " *(critical)*"
        domain = sr.get("domain", "")
        if domain:
            label += f" — domain: `{domain}`"
        st.markdown(label)

        # In Exam mode show full rationale only in results summary
        if not sr["correct"] and mode == MODE_EXAM:
            scenario_steps = scenario.get("steps", [])
            step_obj = next((s for s in scenario_steps if s.get("id") == sr["step_id"]), None)
            if step_obj:
                dps = step_obj.get("decision_points", [])
                if dps:
                    dp = dps[0]
                    chosen_opt = next(
                        (o for o in dp.get("options", []) if o["id"] == sr.get("chosen")), None
                    )
                    if chosen_opt:
                        original_feedback = chosen_opt.get("feedback", "")
                        original_rationale = chosen_opt.get("rationale")
                        if original_feedback:
                            st.markdown(f"  > {original_feedback}")
                        if original_rationale:
                            st.markdown(f"  > **Exam rationale:** {original_rationale}")

    st.divider()

    # Communication checkpoints summary
    comm_results = scores.get("comm_points_earned", 0)
    comm_total = scores.get("comm_points_total", 0)
    if comm_total > 0:
        st.markdown(
            f"### Communication & Professionalism: {comm_results}/{comm_total} points "
            f"({scores.get('communication_score', 0)}%)"
        )
        comms = scenario.get("communication_checkpoints", [])
        for comm in comms:
            comm_id = comm.get("id")
            chosen = st.session_state.get("lab_comm_answers", {}).get(comm_id)
            correct_opt = comm.get("correct_option")
            is_correct = chosen == correct_opt
            icon = "✅" if is_correct else "❌"
            st.markdown(f"{icon} {comm.get('prompt', comm_id)}")

        st.divider()

    # Curriculum mapping for standards alignment
    mapping = load_curriculum_mapping()
    scenario_id = scenario.get("id", "")
    prometric_title = (
        mapping.get("scenario_mappings", {})
        .get(scenario_id, {})
        .get("prometric_skill_title", "")
    )
    if prometric_title:
        st.markdown(f"📋 **Prometric skill evaluated:** _{prometric_title}_")

    st.divider()

    # Next steps and remediation
    st.markdown("### 📌 Recommendations & Remediation")
    next_steps = build_next_steps_text(scores, mode)
    for rec in next_steps:
        st.markdown(f"- {rec}")

    # Targeted remediation table
    remediation = scores.get("remediation_targets", [])
    if remediation:
        st.markdown("#### Targeted Review")
        rem_rows = []
        for r in remediation:
            rem_rows.append({
                "Step": r.get("step_title", ""),
                "Module": r.get("module", ""),
                "Topic": r.get("topic", ""),
                "Exam Domain": r.get("exam_domain", ""),
                "Prometric Skill": r.get("prometric_skill", ""),
            })
        # Use st.dataframe for clean tabular display
        import pandas as pd  # noqa: PLC0415 – deferred import to keep top-level lightweight

        st.dataframe(
            pd.DataFrame(rem_rows),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Retry this scenario", type="primary"):
            scenario_id_saved = st.session_state.get("lab_scenario_id")
            mode_saved = st.session_state.get("lab_mode", MODE_COACH)
            reset_lab_session(st.session_state)
            init_lab_session(st.session_state, scenario_id_saved, mode_saved)
            st.rerun()
    with col2:
        if st.button("📋 Choose another scenario"):
            reset_lab_session(st.session_state)
            st.rerun()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _is_at_start() -> bool:
    """Return True if the lab state indicates no simulation is in progress."""
    return (
        st.session_state.get("lab_scenario_id") is None
        or (
            st.session_state.get("lab_step_index", 0) == 0
            and not st.session_state.get("lab_step_answers")
            and not st.session_state.get("lab_complete")
        )
    )
