"""My Progress – exam performance analytics dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from db import get_quiz_stats_by_domain, get_quiz_trend

# NATCEP exam domains (canonical order for the radar chart)
NATCEP_DOMAINS = [
    "Physical Care Skills",
    "Psychosocial Care Skills",
    "Role of the Nurse Aide",
    "Safety and Emergency",
    "Infection Control",
]

# Minimum passing score for the NATCEP written exam (Texas standard)
PASSING_PCT = 70.0


# ---------------------------------------------------------------------------
# Domain-level study recommendations
# ---------------------------------------------------------------------------
_RECOMMENDATIONS: dict[str, str] = {
    "Physical Care Skills": (
        "Review positioning, vital-sign measurement, range-of-motion exercises, "
        "and personal-care procedures. Practice the skill-lab simulations."
    ),
    "Psychosocial Care Skills": (
        "Study resident rights, communication techniques, cultural sensitivity, "
        "and supporting residents with mental-health or cognitive challenges."
    ),
    "Role of the Nurse Aide": (
        "Focus on scope-of-practice boundaries, mandatory-reporting obligations, "
        "the chain of command, and documentation standards."
    ),
    "Safety and Emergency": (
        "Drill RACE/PASS fire procedures, OSHA hazard protocols, fall prevention, "
        "restraint guidelines, and emergency response steps."
    ),
    "Infection Control": (
        "Practice hand-hygiene steps, PPE doffing order, isolation precaution types, "
        "and transmission-based precaution guidelines."
    ),
}


# ---------------------------------------------------------------------------
# Main show() entry point
# ---------------------------------------------------------------------------
def show() -> None:
    st.title("📊 My Progress")
    st.caption("Personalized exam-readiness analytics based on your quiz history")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please **sign in** on the Home page to view your progress.")
        return

    domain_stats = get_quiz_stats_by_domain(user_id)
    trend_data = get_quiz_trend(user_id)

    if not domain_stats and not trend_data:
        st.info(
            "No quiz attempts recorded yet. "
            "Head over to **📚 Exam Prep** and take a quiz to start tracking your progress!"
        )
        if st.button("Go to Exam Prep →", key="prog_go_exam"):
            st.session_state["nav_target"] = "exam_prep"
            st.rerun()
        return

    # ── Summary metrics ──────────────────────────────────────────────────────
    readiness_score = _calc_readiness_score(domain_stats)
    total_attempts = sum(s["attempts"] for s in domain_stats)
    total_questions = sum(s["total_questions"] for s in domain_stats)

    col1, col2, col3 = st.columns(3)
    col1.metric("Exam Readiness Score", f"{readiness_score:.0f}%")
    col2.metric("Total Quizzes Taken", total_attempts)
    col3.metric("Questions Answered", total_questions)

    _render_readiness_bar(readiness_score)

    st.divider()

    # ── Domain breakdown columns ─────────────────────────────────────────────
    col_chart, col_table = st.columns([1, 1], gap="large")

    with col_chart:
        st.subheader("Domain Radar")
        _render_radar(domain_stats)

    with col_table:
        st.subheader("Domain Scores")
        _render_domain_table(domain_stats)

    # ── Score trend over time ────────────────────────────────────────────────
    if len(trend_data) >= 2:
        st.divider()
        st.subheader("Score Trend Over Time")
        _render_trend(trend_data)

    # ── Strongest / weakest callouts ─────────────────────────────────────────
    if domain_stats:
        st.divider()
        _render_strength_callouts(domain_stats)

    # ── Study recommendations ─────────────────────────────────────────────────
    st.divider()
    _render_recommendations(domain_stats)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _calc_readiness_score(stats: list[dict]) -> float:
    """Weighted average across all attempted domains (by questions answered).

    Domains not yet attempted default to 0 %, pulling the score toward 0
    until all domains have been practised.
    """
    if not stats:
        return 0.0
    total_weight = sum(s["total_questions"] for s in stats)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(
        s["avg_pct"] * s["total_questions"] for s in stats
    )
    return round(weighted_sum / total_weight, 1)


def _render_readiness_bar(score: float) -> None:
    if score >= PASSING_PCT:
        color = "green"
        label = f"🎉 {score:.0f}% — On track to pass!"
    elif score >= 50:
        color = "orange"
        label = f"⚠️ {score:.0f}% — Getting closer, keep studying!"
    else:
        color = "red"
        label = f"📚 {score:.0f}% — More practice needed."

    st.markdown(
        f"""
        <div style="background:#E8E0D4;border-radius:8px;overflow:hidden;
                    height:18px;margin-bottom:6px;">
          <div style="width:{min(score,100):.1f}%;height:100%;
                      background:{'#2D7A2D' if color=='green'
                                   else '#C47A00' if color=='orange'
                                   else '#A01020'};
                      border-radius:8px;transition:width 0.5s;">
          </div>
        </div>
        <p style="margin:0 0 4px 0;font-size:0.92rem;color:#333;">{label}</p>
        """,
        unsafe_allow_html=True,
    )


def _render_radar(stats: list[dict]) -> None:
    """Plotly radar/spider chart of average % per NATCEP domain."""
    stat_map = {s["domain"]: s["avg_pct"] for s in stats}

    # Close the polygon by repeating the first category
    categories = NATCEP_DOMAINS + [NATCEP_DOMAINS[0]]
    values = [stat_map.get(d, 0.0) for d in NATCEP_DOMAINS]
    values_closed = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories,
            fill="toself",
            fillcolor="rgba(90, 12, 26, 0.18)",
            line=dict(color="#5A0C1A", width=2),
            name="Avg Score %",
        )
    )
    # Passing threshold ring
    fig.add_trace(
        go.Scatterpolar(
            r=[PASSING_PCT] * len(categories),
            theta=categories,
            mode="lines",
            line=dict(color="#9E6C00", width=1.5, dash="dot"),
            name=f"Passing ({PASSING_PCT:.0f}%)",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="#FEFBF5",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9),
                gridcolor="#D4C3A8",
            ),
            angularaxis=dict(gridcolor="#D4C3A8"),
        ),
        showlegend=True,
        legend=dict(font=dict(size=10)),
        margin=dict(l=30, r=30, t=30, b=30),
        paper_bgcolor="#F5EDE0",
        plot_bgcolor="#F5EDE0",
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_domain_table(stats: list[dict]) -> None:
    """Display a styled table of domain stats."""
    if not stats:
        st.info("Take quizzes in specific domains to see per-domain scores.")
        return

    stat_map = {s["domain"]: s for s in stats}
    rows = []
    for domain in NATCEP_DOMAINS:
        s = stat_map.get(domain)
        if s:
            badge = "✅" if s["avg_pct"] >= PASSING_PCT else "⚠️"
            rows.append({
                "Domain": domain,
                "Avg %": f"{s['avg_pct']:.0f}%",
                "Best %": f"{s['best_pct']:.0f}%",
                "Quizzes": s["attempts"],
                "Status": badge,
            })
        else:
            rows.append({
                "Domain": domain,
                "Avg %": "—",
                "Best %": "—",
                "Quizzes": 0,
                "Status": "🔲",
            })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_trend(trend_data: list[dict]) -> None:
    """Line chart of quiz score % over time."""
    df = pd.DataFrame(trend_data)
    df["taken_at"] = pd.to_datetime(df["taken_at"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["taken_at"],
            y=df["pct"],
            mode="lines+markers",
            line=dict(color="#5A0C1A", width=2),
            marker=dict(color="#9E6C00", size=7),
            name="Score %",
            hovertemplate="%{x|%b %d, %Y}<br>%{y:.0f}%<extra></extra>",
        )
    )
    # Passing line
    fig.add_hline(
        y=PASSING_PCT,
        line_dash="dot",
        line_color="#9E6C00",
        annotation_text=f"Passing ({PASSING_PCT:.0f}%)",
        annotation_position="bottom right",
    )
    fig.update_layout(
        xaxis=dict(title="Date", gridcolor="#D4C3A8"),
        yaxis=dict(title="Score %", range=[0, 105], gridcolor="#D4C3A8"),
        paper_bgcolor="#F5EDE0",
        plot_bgcolor="#F5EDE0",
        margin=dict(l=40, r=20, t=20, b=40),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_strength_callouts(stats: list[dict]) -> None:
    attempted = [s for s in stats if s["attempts"] > 0]
    if not attempted:
        return

    strongest = max(attempted, key=lambda s: s["avg_pct"])
    weakest = min(attempted, key=lambda s: s["avg_pct"])

    c1, c2 = st.columns(2)
    with c1:
        st.success(
            f"🏆 **Strongest domain:** {strongest['domain']}  \n"
            f"Avg score: **{strongest['avg_pct']:.0f}%** over {strongest['attempts']} quiz(zes)"
        )
    with c2:
        if weakest["avg_pct"] < PASSING_PCT:
            st.error(
                f"📌 **Needs attention:** {weakest['domain']}  \n"
                f"Avg score: **{weakest['avg_pct']:.0f}%** — below passing threshold"
            )
        else:
            st.info(
                f"📌 **Keep it up:** {weakest['domain']}  \n"
                f"Avg score: **{weakest['avg_pct']:.0f}%** — room to grow further"
            )


def _render_recommendations(stats: list[dict]) -> None:
    st.subheader("📋 Study Recommendations")

    stat_map = {s["domain"]: s for s in stats}

    # Domains below passing or not yet attempted — prioritised study targets
    needs_work = [
        d for d in NATCEP_DOMAINS
        if d not in stat_map or stat_map[d]["avg_pct"] < PASSING_PCT
    ]

    if not needs_work:
        st.success(
            "🎉 You're scoring above the passing threshold in every practised domain! "
            "Continue reviewing to maintain your readiness."
        )
        return

    for domain in needs_work:
        s = stat_map.get(domain)
        if s:
            label = f"⚠️ {domain} — avg {s['avg_pct']:.0f}% ({s['attempts']} quiz attempt(s))"
        else:
            label = f"🔲 {domain} — not yet practised"

        with st.expander(label, expanded=False):
            st.markdown(_RECOMMENDATIONS.get(domain, "Review course materials for this domain."))
            if st.button(
                f"📚 Practice {domain} now",
                key=f"rec_btn_{domain.replace(' ', '_')}",
            ):
                st.session_state["nav_target"] = "exam_prep"
                st.rerun()
