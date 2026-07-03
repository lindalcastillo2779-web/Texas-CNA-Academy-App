"""Clinical Skills Lab – Prometric/NATCEP-aligned interactive CNA skill simulations.

Aligned to:
  • Texas HHSC NATCEP Curriculum 2024 (TAC Title 26, Chapter 95)
  • Prometric CNA Skills Evaluation Checklist (Texas pool, 22 skills)
  • TULIP (Texas Unified Licensure Information Portal) reporting standards
  • 2023 AHA/ACC Blood Pressure Guidelines incorporated in HHSC 2024 curriculum
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.lab_engine import (
    build_next_steps_text,
    compute_pre_check_score,
    compute_scores,
    evaluate_comm_answer,
    evaluate_pre_check_answer,
    evaluate_step_answer,
    get_pre_check_questions,
    has_pre_knowledge_check,
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
MODE_EXAM  = "exam"

_MODE_EMOJI   = {MODE_COACH: "🏋️", MODE_EXAM: "🎓"}
_MODE_LABEL   = {MODE_COACH: "🏋️ Coach Mode", MODE_EXAM: "🎓 Exam Mode"}
_MODE_COLOR   = {MODE_COACH: "#1a6b3c", MODE_EXAM: "#8b1a1a"}

_DOMAIN_LABELS = {
    "IC":  "🦠 Infection Control",
    "SE":  "🛡️ Safety & Emergency",
    "BNS": "🩺 Basic Nursing Skills",
    "CD":  "📝 Communication & Documentation",
    "PR":  "👔 Professional Role",
    "RC":  "🔄 Restorative Care",
    "RR":  "⚖️ Residents' Rights",
}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def show() -> None:
    st.title("🧪 Clinical Skills Lab")
    st.caption(
        "Interactive CNA skill simulations — aligned to **Prometric, Pearson VUE, "
        "Texas HHSC NATCEP 2024**, and **TULIP** standards"
    )

    _render_intro_expander()
    st.divider()

    phase = st.session_state.get("lab_phase", "selection")

    if phase == "selection":
        _render_selection_screen()
    elif phase == "briefing":
        _render_scene_briefing()
    elif phase == "pre_check":
        _render_pre_knowledge_check()
    elif phase == "simulation":
        _render_simulation()
    elif phase == "complete":
        _render_results()
    else:
        _render_selection_screen()


# ---------------------------------------------------------------------------
# How-to expander
# ---------------------------------------------------------------------------


def _render_intro_expander() -> None:
    with st.expander("ℹ️ How to use the Clinical Skills Lab — click to expand", expanded=False):
        st.markdown("""
### What is the Clinical Skills Lab?

Scenario-based, step-by-step skill simulations that match the **Prometric CNA skills exam format**
used in Texas. Each scenario places you in a real Texas nursing-facility setting with a fictional
resident and walks you through the exact checklist a Prometric examiner follows.

### Two practice modes

| Mode | When to use | Hints | Feedback |
|------|-------------|-------|----------|
| 🏋️ **Coach Mode** | First-time practice, learning rationale | ✅ Theory facts + rationale | Immediate after every step |
| 🎓 **Exam Mode** | Self-assessment, exam-readiness check | ❌ None — mirrors real exam | Summary only after completion |

**Workflow:** Coach Mode first → understand every step → switch to Exam Mode to test readiness.

### Scoring model (Prometric-aligned)

| Component | Weight | Must achieve |
|-----------|--------|-------------|
| ✅ Checklist score | 40 % | ≥ 75 % |
| 🚨 Critical-step score | 40 % | **100 %** — any miss = automatic Prometric failure |
| 💬 Communication score | 20 % | ≥ 75 % |
| 🎯 **Overall** | 100 % | **≥ 75 % AND all critical steps passed** |

### What each session contains

1. **Scene briefing** — resident profile, clinical context, your role  
2. **Pre-simulation knowledge check** — 3 theory questions (graded, Coach Mode)  
3. **Skill simulation** — step-by-step decision points with Prometric-style choices  
4. **Communication checkpoints** — resident interaction score  
5. **Full results** — score breakdown, step review, curriculum map, remediation plan  

### Adding new scenarios

Add a JSON file to `knowledge/lab_scenarios/`, register it in `utils/lab_engine.py`
(`_SCENARIO_FILES`), and add step mappings to `curriculum_mapping.json`.
        """)


# ---------------------------------------------------------------------------
# Scenario / mode selection
# ---------------------------------------------------------------------------


def _render_selection_screen() -> None:
    scenarios = list_scenarios()
    if not scenarios:
        st.error("No scenarios found. Check `knowledge/lab_scenarios/` for valid JSON files.")
        return

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.subheader("1️⃣  Choose a scenario")
        scenario_map = {s["title"]: s["id"] for s in scenarios}
        selected_title = st.radio(
            "scenario",
            options=list(scenario_map.keys()),
            label_visibility="collapsed",
        )
        selected_id = scenario_map[selected_title]
        sel = next((s for s in scenarios if s["id"] == selected_id), {})

        # Scenario detail card
        with st.container(border=True):
            st.markdown(f"**{sel.get('title', '')}**")
            st.markdown(f"_{sel.get('description', '')}_")
            domains = sel.get("natcep_domains", [])
            if domains:
                st.markdown("**NATCEP domains:** " + " · ".join(f"`{d}`" for d in domains))
            prom = sel.get("prometric_skill", "")
            if prom:
                st.markdown(f"**Prometric skill:** {prom}")
            mins = sel.get("estimated_minutes", 0)
            if mins:
                st.caption(f"⏱ Estimated: {mins} min including pre-check and debrief")

    with col_right:
        st.subheader("2️⃣  Choose a mode")
        mode_choice = st.radio(
            "mode",
            options=[_MODE_LABEL[MODE_COACH], _MODE_LABEL[MODE_EXAM]],
            label_visibility="collapsed",
        )
        mode = MODE_COACH if MODE_COACH in mode_choice else MODE_EXAM

        with st.container(border=True):
            if mode == MODE_COACH:
                st.markdown("### 🏋️ Coach Mode")
                st.markdown("""
- Full hints and theory facts after every step  
- Immediate feedback with exam rationale  
- Great for first-time practice  
- Pre-check score shown as you go  
                """)
            else:
                st.markdown("### 🎓 Exam Mode")
                st.markdown("""
- **No hints or rationale during the attempt**  
- Mirrors actual Prometric exam conditions  
- Full feedback appears in the final summary only  
- Use after you've mastered Coach Mode  
                """)

        st.divider()
        mapping = load_curriculum_mapping()
        pool = mapping.get("prometric_skills_pool_2024", [])
        if pool:
            with st.expander("📋 Full Prometric TX Skills Pool (22 skills)", expanded=False):
                for i, skill in enumerate(pool, 1):
                    st.markdown(f"{i}. {skill}")

    st.divider()
    if st.button("▶️ Start Simulation", type="primary", use_container_width=True):
        init_lab_session(st.session_state, selected_id, mode)
        st.rerun()


# ---------------------------------------------------------------------------
# Scene briefing
# ---------------------------------------------------------------------------


def _render_scene_briefing() -> None:
    scenario = st.session_state.get("lab_scenario", {})
    mode     = st.session_state.get("lab_mode", MODE_COACH)
    briefing = scenario.get("scene_briefing", {})
    alignment = scenario.get("texas_2024_alignment", {})

    _render_phase_header("Scene Briefing", 1, 4, mode)

    col_card, col_obj = st.columns([2, 1], gap="large")

    with col_card:
        st.markdown("### 🏥 Clinical Setting")
        with st.container(border=True):
            facility = briefing.get("facility", "")
            if facility:
                st.markdown(f"**Facility:** {facility}")

            res_name = briefing.get("resident_name", "")
            res_age  = briefing.get("resident_age", "")
            room     = briefing.get("room", "")
            if res_name:
                st.markdown(f"**Resident:** {res_name}, Age {res_age} — {room}")

            dx = briefing.get("primary_diagnosis", "")
            if dx:
                st.markdown(f"**Diagnosis:** {dx}")

            iso = briefing.get("isolation_status", "")
            fall = briefing.get("fall_risk", "")
            if iso:
                st.error(f"⚠️ Isolation: {iso}")
            if fall:
                st.warning(f"⚠️ Fall Risk: {fall}")

            care_notes = briefing.get("care_plan_notes", "")
            if care_notes:
                st.markdown("**Care Plan Notes:**")
                st.info(care_notes)

        st.markdown("### 🎭 Your Role")
        role = briefing.get("your_role", "")
        if role:
            st.markdown(role)

        st.markdown("### 🖼️ Scene Description")
        scene = briefing.get("scene_description", "")
        if scene:
            st.markdown(f"> {scene}")

    with col_obj:
        st.markdown("### 🎯 Learning Objectives")
        objs = briefing.get("learning_objectives", [])
        for obj in objs:
            st.markdown(f"- {obj}")

        st.divider()
        st.markdown("### 📋 Standards Alignment")
        with st.container(border=True):
            tac = alignment.get("tac_reference", "")
            sec = alignment.get("natcep_curriculum_section", "")
            prom = alignment.get("prometric_skill_title", "")
            tulip = alignment.get("tulip_relevance", "")
            if tac:
                st.caption(f"📜 {tac}")
            if sec:
                st.caption(f"📚 {sec}")
            if prom:
                st.markdown(f"**Prometric Skill:** _{prom}_")
            if alignment.get("prometric_skill_always_tested"):
                st.success("🔴 **Always tested** on every Prometric exam")
            if tulip:
                with st.expander("🔑 TULIP relevance"):
                    st.markdown(tulip)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⛔ Cancel — choose another scenario"):
            reset_lab_session(st.session_state)
            st.rerun()
    with col2:
        pre_check_label = (
            "▶️ Continue to Pre-Simulation Knowledge Check"
            if has_pre_knowledge_check(scenario)
            else "▶️ Begin Simulation"
        )
        if st.button(pre_check_label, type="primary", use_container_width=True):
            if has_pre_knowledge_check(scenario):
                st.session_state["lab_phase"] = "pre_check"
            else:
                st.session_state["lab_phase"] = "simulation"
            st.rerun()


# ---------------------------------------------------------------------------
# Pre-simulation knowledge check (Labster-style theory quiz)
# ---------------------------------------------------------------------------


def _render_pre_knowledge_check() -> None:
    scenario  = st.session_state.get("lab_scenario", {})
    mode      = st.session_state.get("lab_mode", MODE_COACH)
    questions = get_pre_check_questions(scenario)

    if not questions:
        st.session_state["lab_phase"] = "simulation"
        st.rerun()
        return

    q_index = st.session_state.get("lab_pre_check_index", 0)

    _render_phase_header("Pre-Simulation Knowledge Check", 2, 4, mode)

    st.markdown(
        "Answer these questions to confirm your foundational knowledge before the skill simulation. "
        "In **Coach Mode** you see immediate explanations. In **Exam Mode** results appear in the final summary."
    )

    if q_index >= len(questions):
        # All questions answered — show summary and continue
        answers  = st.session_state.get("lab_pre_check_answers", {})
        result   = compute_pre_check_score(questions, answers)
        pct      = result["pct"]
        correct  = result["correct"]
        total    = result["total"]

        st.divider()
        st.markdown(f"### Pre-Check Complete: {correct}/{total} ({pct}%)")
        if pct >= 67:
            st.success("✅ Strong foundation — you're ready to begin the skill simulation.")
        else:
            st.warning(
                "⚠️ Some gaps in foundational knowledge. In Coach Mode, the theory facts "
                "during each step will help reinforce these concepts."
            )

        st.divider()
        if st.button("▶️ Begin Skill Simulation", type="primary", use_container_width=True):
            st.session_state["lab_pre_check_score"] = result
            st.session_state["lab_phase"] = "simulation"
            st.rerun()
        return

    question    = questions[q_index]
    q_id        = question.get("id")
    options_raw = question.get("options", [])
    option_labels = [f"{o['id']}) {o['text']}" for o in options_raw]

    _render_progress_bar(q_index, len(questions), label="Knowledge Check")

    with st.container(border=True):
        st.markdown(f"**Question {q_index + 1} of {len(questions)}**")
        st.markdown(f"#### {question.get('question', '')}")

        # Show Texas standard reference in Coach mode
        if mode == MODE_COACH and question.get("texas_standard"):
            st.caption(f"📜 Standard: {question['texas_standard']}")

        chosen_label = st.radio(
            "Select your answer:",
            options=option_labels,
            key=f"pre_check_{q_id}",
            label_visibility="collapsed",
        )
        chosen_id = chosen_label.split(")")[0].strip()

    if st.button("✔️ Submit Answer", key=f"submit_pc_{q_id}", type="primary"):
        result = evaluate_pre_check_answer(question, chosen_id)
        st.session_state["lab_pre_check_answers"][q_id] = chosen_id

        if result["correct"]:
            st.success(f"✅ **Correct!**")
        else:
            if mode == MODE_COACH:
                st.error(f"❌ **Incorrect.** The correct answer was: _{result['correct_text']}_")
            else:
                st.error("❌ Incorrect. Review in your final summary.")

        if mode == MODE_COACH and result.get("explanation"):
            with st.expander("📖 Explanation (Texas HHSC 2024 Standard)"):
                st.markdown(result["explanation"])

        st.session_state["lab_pre_check_index"] = q_index + 1
        if st.button("Next Question →", key=f"next_pc_{q_id}"):
            st.rerun()
        else:
            st.rerun()


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------


def _render_simulation() -> None:
    scenario   = st.session_state.get("lab_scenario", {})
    mode       = st.session_state.get("lab_mode", MODE_COACH)
    step_index = st.session_state.get("lab_step_index", 0)
    steps      = scenario.get("steps", [])
    comms      = scenario.get("communication_checkpoints", [])
    total      = len(steps) + len(comms)

    _render_phase_header("Skill Simulation", 3, 4, mode)
    _render_progress_bar(step_index, total, label="Simulation")

    # Resident sidebar card
    briefing = scenario.get("scene_briefing", {})
    if briefing:
        with st.sidebar:
            st.divider()
            st.markdown("**👤 Resident Profile**")
            st.caption(briefing.get("resident_name", ""))
            st.caption(f"Age {briefing.get('resident_age', '')}")
            dx = briefing.get("primary_diagnosis", "")
            if dx:
                st.caption(dx[:80] + ("…" if len(dx) > 80 else ""))
            iso = briefing.get("isolation_status", "")
            fall = briefing.get("fall_risk", "")
            if iso:
                st.sidebar.error(f"⚠️ {iso[:50]}")
            if fall:
                st.sidebar.warning(f"⚠️ Fall: {fall[:40]}")
            st.divider()

    col_main, col_info = st.columns([3, 1], gap="large")

    with col_main:
        if step_index < len(steps):
            _render_step(steps[step_index], step_index, mode)
        elif (step_index - len(steps)) < len(comms):
            _render_comm_checkpoint(comms[step_index - len(steps)], step_index - len(steps), mode)
        else:
            _finalise(scenario, mode)

    with col_info:
        _render_step_legend(steps, comms, step_index)

    # Abandon button (bottom)
    st.divider()
    if st.button("⛔ Abandon simulation", key="abandon_sim"):
        reset_lab_session(st.session_state)
        st.rerun()


def _render_step_legend(steps, comms, current_index):
    st.markdown("**📍 Progress**")
    for i, s in enumerate(steps):
        crit = "🚨" if s.get("critical") else "📋"
        if i < current_index:
            answered = st.session_state.get("lab_step_answers", {}).get(s["id"])
            correct_opt = s.get("decision_points", [{}])[0].get("correct_option") if s.get("decision_points") else None
            icon = "✅" if answered == correct_opt else "❌"
        elif i == current_index:
            icon = "▶️"
        else:
            icon = "⬜"
        st.caption(f"{icon} {crit} {s.get('title', '')[:35]}")

    if comms:
        st.caption("**💬 Communication**")
        for j, c in enumerate(comms):
            ci = len(steps) + j
            if ci < current_index:
                icon = "✅"
            elif ci == current_index:
                icon = "▶️"
            else:
                icon = "⬜"
            st.caption(f"{icon} {c.get('prompt', '')[:35]}…")


def _render_step(step: dict, step_index: int, mode: str) -> None:
    step_id  = step.get("id")
    is_crit  = step.get("critical", False)
    dps      = step.get("decision_points", [])
    if not dps:
        st.session_state["lab_step_index"] += 1
        st.rerun()
        return

    dp = dps[0]

    # Critical badge
    if is_crit:
        st.error("🚨 **CRITICAL STEP** — Prometric automatic failure if missed or incorrect")
    else:
        st.info("�� **Skill Step**")

    st.markdown(f"### Step {step_index + 1}: {step.get('title', '')}")
    st.markdown(step.get("instruction", ""))

    # Coach Mode: theory knowledge fact
    if mode == MODE_COACH and step.get("knowledge_fact"):
        with st.expander("💡 Theory & Context (tap to read)", expanded=True):
            st.markdown(step["knowledge_fact"])

    # Exam tip (always shown — prepares students for examiner behavior)
    if step.get("exam_tip"):
        with st.expander("🎯 Prometric Exam Tip", expanded=(mode == MODE_COACH)):
            st.markdown(step["exam_tip"])

    st.divider()
    options      = dp.get("options", [])
    option_labels = [f"{o['id']}) {o['text']}" for o in options]

    chosen_label = st.radio(
        dp.get("question", "Select the best answer:"),
        options=option_labels,
        key=f"lab_choice_{step_id}",
    )
    chosen_id = chosen_label.split(")")[0].strip()

    if st.button("✔️ Submit Answer", key=f"submit_{step_id}", type="primary"):
        result = evaluate_step_answer(step, 0, chosen_id, mode)
        st.session_state["lab_step_answers"][step_id] = chosen_id

        if result["correct"]:
            st.success(result["feedback"])
        else:
            st.error(result["feedback"])
            if mode == MODE_COACH:
                if result.get("rationale"):
                    st.markdown(f"**📖 Exam Rationale:** {result['rationale']}")
                if result.get("consequence"):
                    st.warning(f"**⚠️ Clinical Consequence:** {result['consequence']}")

        st.session_state["lab_step_index"] += 1
        st.button("Next Step →", key=f"next_{step_id}", on_click=lambda: None)
        st.rerun()


def _render_comm_checkpoint(comm: dict, comm_index: int, mode: str) -> None:
    comm_id = comm.get("id")

    st.info("💬 **Communication & Professionalism Checkpoint**")
    st.markdown(f"### {comm.get('prompt', '')}")

    options = comm.get("options", [])
    option_labels = [f"{o['id']}) {o['text']}" for o in options]

    chosen_label = st.radio(
        "Your answer:",
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


def _finalise(scenario: dict, mode: str) -> None:
    mapping = load_curriculum_mapping()
    scores  = compute_scores(
        scenario,
        st.session_state.get("lab_step_answers", {}),
        st.session_state.get("lab_comm_answers", {}),
        mapping,
    )
    st.session_state["lab_scores"]  = scores
    st.session_state["lab_complete"] = True
    st.session_state["lab_phase"]   = "complete"
    st.rerun()


# ---------------------------------------------------------------------------
# Results — tabbed, Labster-style debrief
# ---------------------------------------------------------------------------


def _render_results() -> None:
    scenario = st.session_state.get("lab_scenario", {})
    mode     = st.session_state.get("lab_mode", MODE_COACH)
    scores   = st.session_state.get("lab_scores", {})
    mapping  = load_curriculum_mapping()

    _render_phase_header("Results & Debrief", 4, 4, mode)

    # ---- Pass/fail banner ----
    if scores.get("pass_ready"):
        st.success(
            f"🎉 **Exam Ready!** You passed this skill simulation — "
            f"overall score {scores.get('overall_score')}% with all critical steps correct."
        )
        st.balloons()
    elif not scores.get("all_criticals_passed"):
        st.error(
            "🚨 **Critical Step Failure** — One or more critical steps were missed. "
            "On the Prometric exam this would be an **automatic skill failure**. "
            "Study Coach Mode rationale and retry."
        )
    else:
        st.warning(
            f"📋 Score {scores.get('overall_score')}% — below the 75% passing threshold. "
            "Review the step debrief and remediation below, then retry."
        )

    # ---- Score cards ----
    c1, c2, c3, c4 = st.columns(4)
    _score_card(c1, "✅ Checklist",   scores.get("checklist_score", 0),    "Non-critical technique steps · 40% weight")
    _score_card(c2, "🚨 Critical",    scores.get("critical_step_score", 0), "Must be 100% — any miss = Prometric failure · 40% weight")
    _score_card(c3, "💬 Communication", scores.get("communication_score", 0), "Resident interaction checkpoints · 20% weight")
    _score_card(c4, "🎯 Overall",     scores.get("overall_score", 0),      f"Pass threshold: {scores.get('pass_threshold', 75)}%")

    st.divider()

    # ---- Pre-check summary ----
    pre_score = st.session_state.get("lab_pre_check_score")
    if pre_score:
        pct = pre_score.get("pct", 0)
        c = pre_score.get("correct", 0)
        t = pre_score.get("total", 0)
        st.markdown(
            f"**🧠 Pre-Simulation Knowledge Check:** {c}/{t} ({pct}%) — "
            + ("✅ Strong foundation" if pct >= 67 else "⚠️ Review foundational theory")
        )
        st.divider()

    # ---- Tabs ----
    tab_step, tab_comm, tab_curric, tab_remed = st.tabs([
        "📋 Step Review", "�� Communication", "🗺️ Curriculum Map", "📌 Remediation Plan"
    ])

    with tab_step:
        _render_step_review(scenario, scores, mode)

    with tab_comm:
        _render_comm_review(scenario, scores)

    with tab_curric:
        _render_curriculum_map(scenario, scores, mapping)

    with tab_remed:
        _render_remediation(scores, mode)

    # ---- Retry / restart ----
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Retry (same scenario + mode)", type="primary"):
            sid  = st.session_state.get("lab_scenario_id")
            m    = st.session_state.get("lab_mode", MODE_COACH)
            reset_lab_session(st.session_state)
            init_lab_session(st.session_state, sid, m)
            st.rerun()
    with c2:
        opp_mode = MODE_EXAM if mode == MODE_COACH else MODE_COACH
        if st.button(f"🔀 Switch to {_MODE_LABEL[opp_mode]}"):
            sid = st.session_state.get("lab_scenario_id")
            reset_lab_session(st.session_state)
            init_lab_session(st.session_state, sid, opp_mode)
            st.rerun()
    with c3:
        if st.button("📋 Choose another scenario"):
            reset_lab_session(st.session_state)
            st.rerun()


# ---------------------------------------------------------------------------
# Results sub-sections
# ---------------------------------------------------------------------------


def _render_step_review(scenario: dict, scores: dict, mode: str) -> None:
    st.markdown("### Step-by-Step Performance")
    steps_data = scores.get("step_results", [])
    all_steps  = scenario.get("steps", [])

    for sr in steps_data:
        is_correct = sr["correct"]
        is_crit    = sr["critical"]
        icon = "✅" if is_correct else ("🚨" if is_crit else "❌")
        domain_label = _DOMAIN_LABELS.get(sr.get("domain", ""), sr.get("domain", ""))

        with st.expander(
            f"{icon} **{sr['title']}** {'*(critical)*' if is_crit else ''} — {domain_label}",
            expanded=(not is_correct),
        ):
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**Your answer:** option `{sr.get('chosen', 'N/A')}`")
            col_b.markdown(f"**Correct answer:** option `{sr.get('correct_option', 'N/A')}`")

            if sr.get("curriculum_module") or sr.get("curriculum_topic"):
                st.caption(
                    f"📚 {sr.get('curriculum_module', '')} — {sr.get('curriculum_topic', '')}"
                )
            if sr.get("exam_notes"):
                st.info(f"🎯 **Prometric Note:** {sr['exam_notes']}")

            # In Exam Mode, show full rationale now
            if not is_correct:
                step_obj = next((s for s in all_steps if s.get("id") == sr["step_id"]), None)
                if step_obj:
                    dps = step_obj.get("decision_points", [])
                    if dps:
                        dp = dps[0]
                        chosen_opt = next(
                            (o for o in dp.get("options", []) if o["id"] == sr.get("chosen")), None
                        )
                        if chosen_opt:
                            if chosen_opt.get("feedback"):
                                st.error(chosen_opt["feedback"])
                            if chosen_opt.get("rationale"):
                                st.markdown(f"**📖 Exam Rationale:** {chosen_opt['rationale']}")
                            if chosen_opt.get("consequence"):
                                st.warning(f"**⚠️ Clinical Consequence:** {chosen_opt['consequence']}")


def _render_comm_review(scenario: dict, scores: dict) -> None:
    st.markdown("### Communication & Professionalism Checkpoints")
    comms = scenario.get("communication_checkpoints", [])
    comm_answers = st.session_state.get("lab_comm_answers", {})
    pts_earned = scores.get("comm_points_earned", 0)
    pts_total  = scores.get("comm_points_total", 0)
    comm_pct   = scores.get("communication_score", 0)

    st.markdown(f"**Score: {pts_earned}/{pts_total} points ({comm_pct}%)**")

    for comm in comms:
        comm_id = comm.get("id")
        chosen  = comm_answers.get(comm_id)
        correct = comm.get("correct_option")
        ok      = chosen == correct
        icon    = "✅" if ok else "❌"
        pts     = comm.get("points", 5)

        with st.expander(f"{icon} {comm.get('prompt', comm_id)} (+{pts if ok else 0}/{pts} pts)"):
            if ok:
                st.success(comm.get("feedback_pass", "Checkpoint met."))
            else:
                st.warning(comm.get("feedback_fail", "Checkpoint missed."))
            st.caption(
                "Residents' Rights (Texas HHSC NATCEP 2024, Section X) requires CNAs to "
                "maintain resident dignity, explain procedures, and ensure comfort at every care episode."
            )


def _render_curriculum_map(scenario: dict, scores: dict, mapping: dict) -> None:
    st.markdown("### Texas HHSC 2024 Curriculum & Prometric Standards Map")

    scenario_id  = scenario.get("id", "")
    sc_map       = mapping.get("scenario_mappings", {}).get(scenario_id, {})
    prom_title   = sc_map.get("prometric_skill_title", "")
    always_tested = sc_map.get("always_tested", False)
    tx_section   = sc_map.get("texas_2024_section", "")
    tac_ref      = mapping.get("standards_reference", {}).get("tac_citation", "")

    col1, col2 = st.columns(2)
    with col1:
        if prom_title:
            st.markdown(f"**Prometric Skill:** {prom_title}")
        if always_tested:
            st.error("🔴 This skill is **always tested** on every Prometric exam")
        if tx_section:
            st.markdown(f"**NATCEP 2024 Section:** {tx_section}")
        if tac_ref:
            st.caption(f"📜 {tac_ref}")
    with col2:
        ref = mapping.get("standards_reference", {})
        st.caption(f"📋 Exam: {', '.join(ref.get('exam_boards', []))}")
        st.caption(f"⏱ Clinical training: {ref.get('clinical_training_hours', {}).get('minimum_total', '')} hours minimum")
        st.caption(f"📝 Written exam: {ref.get('written_exam', {}).get('questions', '')} questions, "
                   f"{ref.get('written_exam', {}).get('time_minutes', '')} min, "
                   f"pass ≥{ref.get('written_exam', {}).get('passing_pct', '')}%")

    st.divider()
    st.markdown("**Step-Level Domain Map**")
    step_map = sc_map.get("steps", {})
    rows = []
    for sr in scores.get("step_results", []):
        sm = step_map.get(sr["step_id"], {})
        rows.append({
            "Step": sr["title"],
            "Domain": _DOMAIN_LABELS.get(sm.get("domain", ""), sm.get("domain", "")),
            "Criticality": sm.get("criticality", ""),
            "Module": sm.get("curriculum_module", ""),
            "Passed": "✅" if sr["correct"] else "❌",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Normal vital range reference card
    vr = mapping.get("normal_vital_ranges_2024")
    if vr:
        st.divider()
        with st.expander("📊 2024 Normal Vital Sign Ranges (Texas HHSC / AHA)", expanded=False):
            st.markdown(f"""
| Vital Sign | Normal Range | Abnormal Threshold |
|---|---|---|
| 🌡️ Temperature (oral) | {vr['temperature_oral_f']['min']}–{vr['temperature_oral_f']['max']} °F | Fever ≥{vr['temperature_oral_f']['fever']} °F |
| 💓 Pulse | {vr['pulse_bpm']['min']}–{vr['pulse_bpm']['max']} bpm | Brady <{vr['pulse_bpm']['bradycardia_below']} / Tachy >{vr['pulse_bpm']['tachycardia_above']} |
| 🫁 Respirations | {vr['respirations_per_min']['min']}–{vr['respirations_per_min']['max']} breaths/min | <{vr['respirations_per_min']['bradypnea_below']} or >{vr['respirations_per_min']['tachypnea_above']} |
| ❤️ BP Normal | <{vr['bp_normal_systolic']['max']}/{vr['bp_normal_diastolic']['max']} mmHg | Stage 1 HTN: {vr['bp_stage1_htn']['systolic']}/{vr['bp_stage1_htn']['diastolic']} |
| 🩸 BP Stage 2 HTN | ≥{vr['bp_stage2_htn']['systolic']}/{vr['bp_stage2_htn']['diastolic']} mmHg | Requires immediate reporting |
| 💨 O₂ Saturation | ≥{vr['oxygen_saturation_pct']['normal_min']}% | Report <{vr['oxygen_saturation_pct']['normal_min']}% to nurse |
            """)
            st.caption(f"Source: {vr.get('source', '')}")


def _render_remediation(scores: dict, mode: str) -> None:
    st.markdown("### 📌 Personalised Remediation Plan")
    next_steps = build_next_steps_text(scores, mode)
    for rec in next_steps:
        st.markdown(f"- {rec}")

    remediation = scores.get("remediation_targets", [])
    if remediation:
        st.divider()
        st.markdown("#### Targeted Study Topics")
        rows = []
        for r in remediation:
            rows.append({
                "Missed Step": r.get("step_title", ""),
                "Module": r.get("module", ""),
                "Topic": r.get("topic", ""),
                "Exam Domain": r.get("exam_domain", ""),
                "Prometric Skill": r.get("prometric_skill", ""),
                "Critical": "🚨" if r.get("critical") else "📋",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Prometric skills pool reminder
    mapping = load_curriculum_mapping()
    pool    = mapping.get("prometric_skills_pool_2024", [])
    if pool:
        st.divider()
        with st.expander("📋 Full Prometric Texas Skills Pool — 22 skills", expanded=False):
            cols = st.columns(2)
            half = len(pool) // 2
            for i, skill in enumerate(pool):
                cols[0 if i < half else 1].markdown(f"- {skill}")


# ---------------------------------------------------------------------------
# Shared UI helpers
# ---------------------------------------------------------------------------


def _render_phase_header(phase_name: str, phase_num: int, total_phases: int, mode: str) -> None:
    mode_label = _MODE_LABEL.get(mode, mode)
    st.markdown(
        f"**Phase {phase_num}/{total_phases}:** {phase_name} &nbsp;|&nbsp; "
        f"<span style='color:gray'>{mode_label}</span>",
        unsafe_allow_html=True,
    )


def _render_progress_bar(current: int, total: int, label: str = "") -> None:
    if total > 0:
        pct = min(current / total, 1.0)
        st.progress(pct, text=f"{label}: {current}/{total}")


def _score_card(col, label: str, value: int, help_text: str) -> None:
    delta_color = "normal"
    if value >= 75:
        delta_color = "normal"
    col.metric(label, f"{value}%", help=help_text)
