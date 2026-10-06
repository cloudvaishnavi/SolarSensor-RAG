"""
ui/eval_page.py
---------------
Phase 1 Evaluation Harness — Streamlit UI component.

Renders an expandable section in the main app showing:
  - Baseline metrics table
  - Before vs After comparison
  - Score distribution (bar chart)
  - Per-question results table with colour-coded verdicts

Imported and called by app.py as:
    from ui.eval_page import render_eval_section
    render_eval_section(T)

No existing ui/ or backend/ files are modified.
"""

from __future__ import annotations

import os
import json

import streamlit as st

@st.cache_data(show_spinner=False)
def _cached_baseline_results():
    """Load baseline results once per Streamlit session using st.cache_data."""
    try:
        from eval.runner import load_baseline_results
        return load_baseline_results()
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def _cached_manual_grades():
    """Load manual grades once per Streamlit session using st.cache_data."""
    try:
        from eval.runner import load_manual_grades
        return load_manual_grades()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def _score_color(score: float | None, T: dict, threshold_high=0.8, threshold_low=0.5) -> str:
    if score is None:
        return "#64748B"
    if score >= threshold_high:
        return "#10B981"
    if score >= threshold_low:
        return "#F59E0B"
    return "#EF4444"


def _verdict_badge(category: str, r: dict, T: dict) -> str:
    if category == "adversarial":
        v = r.get("refusal_correct")
        if v == 1:
            return "<span style='background:#0A2E22;color:#10B981;border:1px solid #10B981;border-radius:2px;padding:2px 8px;font-size:0.72rem;font-weight:700;'>✅ Refused</span>"
        elif v == 0:
            return "<span style='background:#2D0A0A;color:#EF4444;border:1px solid #EF4444;border-radius:2px;padding:2px 8px;font-size:0.72rem;font-weight:700;'>❌ Hallucinated</span>"
        return "<span style='color:#64748B;font-size:0.72rem;'>—</span>"
    else:
        faith = r.get("faithfulness", 0) or 0
        relev = r.get("relevance", 0) or 0
        if faith == 1 and relev >= 2:
            return "<span style='background:#0A2E22;color:#10B981;border:1px solid #10B981;border-radius:2px;padding:2px 8px;font-size:0.72rem;font-weight:700;'>✅ Good</span>"
        elif faith == 1 and relev == 1:
            return "<span style='background:#1E1A14;color:#F59E0B;border:1px solid #F59E0B;border-radius:2px;padding:2px 8px;font-size:0.72rem;font-weight:700;'>⚠️ Partial</span>"
        else:
            return "<span style='background:#2D0A0A;color:#EF4444;border:1px solid #EF4444;border-radius:2px;padding:2px 8px;font-size:0.72rem;font-weight:700;'>❌ Poor</span>"


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def render_eval_section(T: dict):
    """
    Renders the Phase 1 Evaluation section as a Streamlit expander.
    Call this from app.py after the main chat UI.
    """
    _baseline_results = _cached_baseline_results()
    _manual_grades    = _cached_manual_grades()

    with st.expander("📊 Phase 1 — Evaluation Harness (Baseline)", expanded=False):

        # Header
        st.markdown(
            "<div style='font-size:0.75rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:0.5px;color:#64748B;margin-bottom:4px;'>"
            "Frozen evaluation set · 27 questions · Dense-only baseline (MMR k=5) · LLM-as-judge faithfulness &amp; relevance"
            "</div>",
            unsafe_allow_html=True,
        )

        if _baseline_results is None:
            st.info(
                "⚙️ Baseline results not yet generated. "
                "Run `python -m eval.runner` from the project root to produce them."
            )
            _render_eval_set_preview(T)
            return

        summary      = _baseline_results.get("summary", {})
        summary_modes = _baseline_results.get("summary_all_modes", {"dense_only": summary})
        per_q        = _baseline_results.get("per_question", [])
        meta         = _baseline_results.get("_meta", {})

        st.caption(
            f"Run at: {meta.get('run_at','—')} · "
            f"Model: {meta.get('model','—')} · "
            f"Retrieval: {meta.get('retrieval','—')}"
        )

        # Top metric cards
        _render_metric_cards(summary, T)

        st.markdown("<hr style='border-color:#2D3748;margin:20px 0;'>", unsafe_allow_html=True)

        # Before vs After table (BUG FIX 2: pass all-modes dict)
        _render_before_after_table(summary_modes, T)

        st.markdown("<hr style='border-color:#2D3748;margin:20px 0;'>", unsafe_allow_html=True)

        # Score distribution
        _render_score_distribution(per_q, T)

        st.markdown("<hr style='border-color:#2D3748;margin:20px 0;'>", unsafe_allow_html=True)

        # Per-question results
        _render_per_question_table(per_q, T)

        st.markdown("<hr style='border-color:#2D3748;margin:20px 0;'>", unsafe_allow_html=True)

        # Manual grades
        _render_manual_grades(T)


# ---------------------------------------------------------------------------
# Sub-renderers
# ---------------------------------------------------------------------------

def _render_metric_cards(summary: dict, T: dict):
    # Values arrive as 0–100 percentages from the fixed load_baseline_results().
    r5          = summary.get("recall_at_5")          # already × 100
    r10         = summary.get("recall_at_10")         # already × 100
    faith_pct   = summary.get("faithfulness_pct")
    relev_pct   = summary.get("relevance_pct")
    refusal_pct = summary.get("refusal_accuracy_pct")

    def _fmt(v):
        return f"{v:.1f}%" if v is not None else "—"

    def _card(label, value, color):
        return (
            f"<div style='background:#232830;border:1px solid #2D3748;"
            f"border-radius:4px;padding:20px 24px;'>"
            f"<div style='font-size:0.7rem;color:#64748B;text-transform:uppercase;"
            f"letter-spacing:0.5px;font-weight:700;margin-bottom:10px;'>{label}</div>"
            f"<div style='font-size:2rem;font-weight:700;color:{color};line-height:1;'>{value}</div>"
            f"</div>"
        )

    cols = st.columns(5)
    # BUG FIX 1: values are already percentages; divide by 100 only for colour
    # thresholding (which expects a 0–1 fraction). Display with _fmt directly.
    cards = [
        ("Recall@5",     _fmt(r5),          _score_color(r5  / 100 if r5  is not None else None, T)),
        ("Recall@10",    _fmt(r10),         _score_color(r10 / 100 if r10 is not None else None, T)),
        ("Faithfulness", _fmt(faith_pct),   _score_color(faith_pct   / 100 if faith_pct   is not None else None, T)),
        ("Relevance",    _fmt(relev_pct),   _score_color(relev_pct   / 100 if relev_pct   is not None else None, T)),
        ("Refusal Acc.", _fmt(refusal_pct), _score_color(refusal_pct / 100 if refusal_pct is not None else None, T)),
    ]
    for col, (label, value, color) in zip(cols, cards):
        col.markdown(_card(label, value, color), unsafe_allow_html=True)


def _render_before_after_table(summary_all_modes: dict, T: dict):
    """
    BUG FIX 2: Render a 4-column table — Metric | Dense Only | Dense+Rerank | Hybrid+Rerank.
    All values come from summary_all_modes (three mode dicts, each with pct values).
    The _(future)_ placeholders are removed; real numbers are shown for every mode.
    """
    st.markdown(
        "<div style='font-weight:700;font-size:0.85rem;color:#F8FAFC;margin-bottom:12px;'>"
        "📈 Before vs After Comparison</div>",
        unsafe_allow_html=True,
    )

    dense       = summary_all_modes.get("dense_only",   {})
    dr          = summary_all_modes.get("dense_rerank",  {})
    hr          = summary_all_modes.get("hybrid_rerank", {})

    def _pct(v):
        return f"{v:.1f}%" if v is not None else "—"

    # (metric label, key in the mode dict)
    metric_keys = [
        ("Recall@5",     "recall_at_5"),
        ("Recall@10",    "recall_at_10"),
        ("Faithfulness", "faithfulness_pct"),
        ("Relevance",    "relevance_pct"),
        ("Refusal Acc.", "refusal_accuracy_pct"),
    ]

    hdr = "font-size:0.72rem;font-weight:700;text-transform:uppercase;color:#64748B;letter-spacing:0.5px;"
    th  = f"style='{hdr}text-align:center;padding:8px 12px;border-bottom:1px solid #2D3748;'"
    table_html = (
        f"<table style='width:100%;border-collapse:collapse;font-size:0.82rem;'>"
        f"<thead><tr>"
        f"<th style='{hdr}text-align:left;padding:8px 12px;border-bottom:1px solid #2D3748;'>Metric</th>"
        f"<th {th}>🔵 Dense Only<br><small style='font-weight:400;'>(Baseline)</small></th>"
        f"<th {th}>🟡 Dense + Rerank</th>"
        f"<th {th}>🟢 Hybrid + Rerank</th>"
        f"</tr></thead><tbody>"
    )

    for label, key in metric_keys:
        v_dense = _pct(dense.get(key))
        v_dr    = _pct(dr.get(key))
        v_hr    = _pct(hr.get(key))
        table_html += (
            f"<tr style='border-bottom:1px solid #2D3748;'>"
            f"<td style='padding:10px 12px;color:#F8FAFC;font-weight:600;'>{label}</td>"
            f"<td style='padding:10px 12px;text-align:center;color:#3B82F6;font-weight:700;'>{v_dense}</td>"
            f"<td style='padding:10px 12px;text-align:center;color:#F59E0B;font-weight:700;'>{v_dr}</td>"
            f"<td style='padding:10px 12px;text-align:center;color:#10B981;font-weight:700;'>{v_hr}</td>"
            f"</tr>"
        )

    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)


def _render_score_distribution(per_q: list, T: dict):
    st.markdown(
        "<div style='font-weight:700;font-size:0.85rem;color:#F8FAFC;margin-bottom:12px;'>"
        "📊 Score Distribution</div>",
        unsafe_allow_html=True,
    )

    # ── Faithfulness + Relevance side by side ───────────────────────────────
    col_faith, col_relev = st.columns(2)

    with col_faith:
        st.caption("Faithfulness (0 = unfaithful, 1 = faithful)")
        faithful   = sum(1 for r in per_q if r.get("faithfulness") == 1)
        unfaithful = sum(1 for r in per_q if r.get("faithfulness") == 0)
        # BUG FIX 1a: use pandas so both bars always render even when one is 0
        try:
            import pandas as pd
            faith_df = pd.DataFrame(
                {"Count": [unfaithful, faithful]},
                index=pd.Index(["Unfaithful (0)", "Faithful (1)"], name="Score"),
            )
            st.bar_chart(faith_df, color="#10B981")
        except ImportError:
            st.bar_chart({"Faithful (1)": faithful, "Unfaithful (0)": unfaithful}, color="#10B981")

    with col_relev:
        st.caption("Relevance score (0–3)")
        # BUG FIX 2: pre-build counts, then wrap in a DataFrame with an
        # explicit categorical index so Streamlit renders all 4 buckets
        # correctly and never inserts a "—" gap for zero-count buckets.
        relev_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        for r in per_q:
            v = r.get("relevance")
            if v is not None and int(v) in relev_counts:
                relev_counts[int(v)] += 1
        try:
            import pandas as pd
            relev_df = pd.DataFrame(
                {"Count": [relev_counts[i] for i in range(4)]},
                index=pd.Index(["0", "1", "2", "3"], name="Score"),
            )
            st.bar_chart(relev_df, color="#3B82F6")
        except ImportError:
            st.bar_chart({str(k): v for k, v in relev_counts.items()}, color="#3B82F6")

    # ── Refusal accuracy (adversarial questions only) ────────────────────────
    adv = [r for r in per_q if r.get("category") == "adversarial"]
    if adv:
        refused_ok   = sum(1 for r in adv if r.get("refusal_correct") == 1)
        hallucinated = sum(1 for r in adv if r.get("refusal_correct") == 0)
        unknown      = len(adv) - refused_ok - hallucinated

        st.caption(f"Refusal accuracy — {len(adv)} adversarial questions")

        # BUG FIX 1b: st.bar_chart collapses when one value is 0 (no visible bar).
        # Replace with styled HTML metric boxes that always render regardless of value.
        def _refusal_box(label: str, count: int, color: str) -> str:
            pct = f"{count / len(adv) * 100:.0f}%" if adv else "—"
            return (
                f"<div style='background:#1A2332;border:1px solid {color};"
                f"border-radius:4px;padding:14px 18px;text-align:center;'>"
                f"<div style='font-size:0.7rem;color:#94A3B8;text-transform:uppercase;"
                f"letter-spacing:0.5px;font-weight:700;margin-bottom:8px;'>{label}</div>"
                f"<div style='font-size:2rem;font-weight:700;color:{color};line-height:1;'>{count}</div>"
                f"<div style='font-size:0.75rem;color:#64748B;margin-top:4px;'>{pct} of adversarial</div>"
                f"</div>"
            )

        cols = st.columns(3 if unknown else 2)
        cols[0].markdown(_refusal_box("✅ Correctly Refused", refused_ok, "#10B981"),   unsafe_allow_html=True)
        cols[1].markdown(_refusal_box("❌ Hallucinated",      hallucinated, "#EF4444"), unsafe_allow_html=True)
        if unknown:
            cols[2].markdown(_refusal_box("❓ Unknown", unknown, "#64748B"), unsafe_allow_html=True)


def _render_per_question_table(per_q: list, T: dict):
    st.markdown(
        "<div style='font-weight:700;font-size:0.85rem;color:#F8FAFC;margin-bottom:12px;'>"
        "🔍 Per-Question Results</div>",
        unsafe_allow_html=True,
    )

    cat_filter = st.selectbox(
        "Filter by category",
        ["All", "factual", "synthesis", "adversarial"],
        key="_eval_cat_filter",
    )
    filtered = per_q if cat_filter == "All" else [r for r in per_q if r["category"] == cat_filter]

    for r in filtered:
        badge = _verdict_badge(r["category"], r, T)
        cat_label = {
            "factual": "🔎 Factual",
            "synthesis": "🔗 Synthesis",
            "adversarial": "🛡️ Adversarial",
        }.get(r["category"], r["category"])

        r5_str  = f"{r['recall_at_5']:.0f}" if r.get("recall_at_5") is not None else "—"
        r10_str = f"{r['recall_at_10']:.0f}" if r.get("recall_at_10") is not None else "—"

        with st.expander(
            f"{r['id']}  ·  {cat_label}  ·  {r['question'][:70]}{'…' if len(r['question'])>70 else ''}",
            expanded=False,
        ):
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Recall@5",  r5_str)
            mc2.metric("Recall@10", r10_str)
            mc3.metric("Faithfulness", str(r.get("faithfulness", "—")))
            mc4.metric("Relevance", str(r.get("relevance", r.get("refusal_correct", "—"))))

            st.markdown(f"**Question:** {r['question']}")
            st.markdown("**System Answer:**")
            st.info(r.get("answer", "—"))

            sources_retrieved = r.get("retrieved_sources", [])
            ideal = r.get("ideal_source_docs", [])
            if sources_retrieved:
                # BUG FIX 3: only label as "none (adversarial)" for actual
                # adversarial questions; non-adversarial with missing ideal docs
                # show a neutral "not recorded" message instead.
                if ideal:
                    ideal_str = "`, `".join(ideal)
                elif r.get("category") == "adversarial":
                    ideal_str = "none (adversarial — no ideal doc expected)"
                else:
                    ideal_str = "not recorded in result file"
                st.markdown(
                    f"**Retrieved:** `{'`, `'.join(sources_retrieved[:5])}`  \n"
                    f"**Ideal:** `{ideal_str}`   {badge}",
                    unsafe_allow_html=True,
                )


def _render_manual_grades(T: dict):
    st.markdown(
        "<div style='font-weight:700;font-size:0.85rem;color:#F8FAFC;margin-bottom:12px;'>"
        "✍️ Manual Grading (Human vs LLM-Judge Agreement)</div>",
        unsafe_allow_html=True,
    )

    _manual_grades = _cached_manual_grades()

    if _manual_grades is None:
        # Info card (no <pre> block — Streamlit strips \n from HTML strings
        # passed to st.markdown, collapsing the JSON to a single line).
        st.markdown(
            "<div style='background:#1A2332;border:1px solid #2D3748;border-left:3px solid #3B82F6;"
            "border-radius:4px;padding:16px 20px;margin-bottom:8px;'>"
            "<div style='color:#F8FAFC;font-weight:600;margin-bottom:6px;'>ℹ️ Manual grading is optional</div>"
            "<div style='color:#94A3B8;font-size:0.82rem;line-height:1.6;'>"
            "No <code>eval/manual_grades.json</code> file was found. "
            "This section shows human-vs-LLM-judge agreement once you record manual verdicts.<br><br>"
            "<b>To enable:</b> create <code>eval/manual_grades.json</code> with this structure:"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        # Use st.code so the JSON is always properly indented and syntax-highlighted
        _json_template = '''{
  "agreement_rate": 0.9,
  "grades": [
    {
      "id": "F01",
      "question": "What is Cost-Save mode?",
      "human_verdict": "Good",
      "llm_verdict": "Good",
      "agrees": true
    }
  ]
}'''
        st.code(_json_template, language="json")
        return

    grades    = _manual_grades.get("grades", [])
    agreement = _manual_grades.get("agreement_rate")

    if agreement is not None:
        st.metric(
            "Human vs LLM-Judge Agreement Rate",
            f"{agreement * 100:.1f}%",
            help="Fraction of manually-graded questions where human verdict matches LLM judge verdict.",
        )

    if grades:
        hdr = "font-size:0.72rem;font-weight:700;text-transform:uppercase;color:#64748B;letter-spacing:0.5px;"
        tbl = (
            f"<table style='width:100%;border-collapse:collapse;font-size:0.8rem;'>"
            f"<thead><tr>"
            f"<th style='{hdr}text-align:left;padding:6px 10px;border-bottom:1px solid #2D3748;'>ID</th>"
            f"<th style='{hdr}text-align:left;padding:6px 10px;border-bottom:1px solid #2D3748;'>Question</th>"
            f"<th style='{hdr}text-align:center;padding:6px 10px;border-bottom:1px solid #2D3748;'>Human</th>"
            f"<th style='{hdr}text-align:center;padding:6px 10px;border-bottom:1px solid #2D3748;'>LLM Judge</th>"
            f"<th style='{hdr}text-align:center;padding:6px 10px;border-bottom:1px solid #2D3748;'>Match?</th>"
            f"</tr></thead><tbody>"
        )
        for g in grades:
            match_icon = "✅" if g.get("agrees") else "❌"
            tbl += (
                f"<tr style='border-bottom:1px solid #2D3748;'>"
                f"<td style='padding:8px 10px;color:#64748B;'>{g.get('id','')}</td>"
                f"<td style='padding:8px 10px;color:#F8FAFC;'>{g.get('question','')[:60]}…</td>"
                f"<td style='padding:8px 10px;text-align:center;'>{g.get('human_verdict','—')}</td>"
                f"<td style='padding:8px 10px;text-align:center;'>{g.get('llm_verdict','—')}</td>"
                f"<td style='padding:8px 10px;text-align:center;'>{match_icon}</td>"
                f"</tr>"
            )
        tbl += "</tbody></table>"
        st.markdown(tbl, unsafe_allow_html=True)


def _render_eval_set_preview(T: dict):
    """Show a preview of the frozen eval set when no results exist yet."""
    try:
        _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        eval_path = os.path.join(_root, "data", "eval_set.json")
        with open(eval_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return

    meta      = data.get("_meta", {})
    questions = data.get("questions", [])

    st.markdown(
        f"<div style='font-weight:700;font-size:0.82rem;color:#F8FAFC;margin:12px 0 6px;'>"
        f"Frozen Eval Set Preview — {meta.get('total', len(questions))} questions</div>",
        unsafe_allow_html=True,
    )
    cats = meta.get("categories", {})
    st.caption(
        f"Factual: {cats.get('factual','?')} · "
        f"Synthesis: {cats.get('synthesis','?')} · "
        f"Adversarial: {cats.get('adversarial','?')}"
    )
    for q in questions[:5]:
        st.markdown(
            f"- **[{q['id']}]** ({q['category']}) {q['question']}",
            unsafe_allow_html=False,
        )
    if len(questions) > 5:
        st.caption(f"…and {len(questions)-5} more. See `data/eval_set.json`.")
