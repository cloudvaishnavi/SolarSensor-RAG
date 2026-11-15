import streamlit as st
import os
import time
from backend.text_utils import _clean_snippet, _html_escape, _highlight_snippet
from ui.theme import THEMES


def _render_sources(sources, answer=""):
    """Render grounding source cards in an expander."""
    if not sources:
        return
    with st.expander(f"📎 View Grounding Sources ({len(sources)})", expanded=False):
        cols = st.columns(2)
        for i, doc in enumerate(sources[:2]):
            src     = _html_escape(os.path.basename(doc.metadata.get("source", "Unknown")))
            page    = doc.metadata.get("page", "")
            pg_info = f" &middot; Page&nbsp;{page + 1}" if page != "" else ""
            snippet = _highlight_snippet(_clean_snippet(doc.page_content, max_len=300), answer)
            with cols[i % 2]:
                st.markdown(
                    f'<div class="source-card">'
                    f'<div class="source-card-title">'
                    f'📄 {src}'
                    f'<span class="source-card-rank">{pg_info}</span>'
                    f'<span class="source-card-rank">&nbsp;#{i + 1}</span>'
                    f'</div>'
                    f'<div class="source-card-snippet">&ldquo;{snippet}&rdquo;</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        for i, doc in enumerate(sources[2:], start=3):
            src     = _html_escape(os.path.basename(doc.metadata.get("source", "Unknown")))
            page    = doc.metadata.get("page", "")
            pg_info = f" &middot; Page&nbsp;{page + 1}" if page != "" else ""
            snippet = _highlight_snippet(_clean_snippet(doc.page_content, max_len=300), answer)
            st.markdown(
                f'<div class="source-card">'
                f'<div class="source-card-title">'
                f'📄 {src}'
                f'<span class="source-card-rank">{pg_info}</span>'
                f'<span class="source-card-rank">&nbsp;#{i}</span>'
                f'</div>'
                f'<div class="source-card-snippet">&ldquo;{snippet}&rdquo;</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _render_context_chips(sources, answer=""):
    """Compact source preview shown directly above the assistant answer."""
    if not sources:
        return

    theme_name = st.session_state.get("theme", "light")
    T = THEMES.get(theme_name, THEMES["light"])

    # Stitch styled "GROUNDED CONTEXT USED" header
    st.markdown(
        f"<div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;"
        f"letter-spacing:0.8px;color:{T['text_dim']};margin:8px 0 8px 0;'>Grounded Context Used</div>",
        unsafe_allow_html=True,
    )

    # Render source capsule pill chips inline
    chips_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;'>"
    for d in sources[:5]:
        src  = _html_escape(os.path.basename(d.metadata.get("source", "Unknown")))
        page = d.metadata.get("page", "")
        pg   = f" · p.{page + 1}" if page != "" else ""
        chips_html += (
            f"<span style='display:inline-flex;align-items:center;gap:5px;"
            f"background:{T['surface_alt']};border:1px solid {T['border']};border-radius:9999px;"
            f"padding:4px 11px;font-size:0.74rem;color:{T['text_muted']};font-weight:500;'>"
            f"📄 {src}{pg}</span>"
        )
    chips_html += "</div>"
    st.markdown(chips_html, unsafe_allow_html=True)


def _render_feedback_widget(msg_index: int, question: str, answer: str):
    """Show thumbs-up/down + optional comment for a single assistant turn."""
    if "user_feedback" not in st.session_state:
        st.session_state.user_feedback = []

    theme_name = st.session_state.get("theme", "light")
    T = THEMES.get(theme_name, THEMES["light"])

    fb_key  = f"_fb_submitted_{msg_index}"
    already = st.session_state.get(fb_key, False)

    if already:
        recorded = next((f for f in st.session_state.user_feedback if f.get("msg_index") == msg_index), None)
        if recorded:
            emoji = "👍" if recorded["score"] == 1 else "👎"
            st.markdown(
                f"<div class='feedback-row'><span class='feedback-label' style='color:{T['accent']};font-weight:600;'>{emoji} Feedback recorded — thank you!</span></div>",
                unsafe_allow_html=True,
            )
        return

    st.markdown(
        f"<div class='feedback-row' style='display:flex;align-items:center;gap:12px;margin-top:10px;padding-top:10px;border-top:1px solid {T['border']};'>"
        f"<span class='feedback-label' style='font-size:0.75rem;color:{T['text_dim']};font-weight:600;'>Was this answer helpful?</span>",
        unsafe_allow_html=True,
    )
    col_up, col_down, col_comment, col_submit = st.columns([1, 1, 5, 1.5])
    with col_up:
        thumbs_up = st.button("👍", key=f"fb_up_{msg_index}", help="Helpful")
    with col_down:
        thumbs_down = st.button("👎", key=f"fb_down_{msg_index}", help="Not helpful")
    with col_comment:
        comment = st.text_input("Optional comment", key=f"fb_comment_{msg_index}", label_visibility="collapsed", placeholder="Optional feedback comment…")
    with col_submit:
        submit = st.button("Submit", key=f"fb_submit_{msg_index}")
    st.markdown("</div>", unsafe_allow_html=True)

    score = None
    if thumbs_up:
        score = 1
    elif thumbs_down:
        score = 0

    if (score is not None or submit) and score is not None:
        st.session_state.user_feedback.append({
            "msg_index": msg_index,
            "question": question,
            "answer": answer[:200],
            "score": score,
            "comment": comment,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        st.session_state[fb_key] = True
        st.rerun()


def _render_retrieval_mode_badge(retrieval_mode: str, T: dict = None):
    """
    Render a flat pill badge showing the active retrieval mode next to an answer.
    """
    if not retrieval_mode or retrieval_mode == "Dense only":
        return

    theme_name = st.session_state.get("theme", "light")
    T = T or THEMES.get(theme_name, THEMES["light"])

    color_map = {
        "Dense + Rerank":  ("#052E24", "rgba(8, 127, 91, 0.10)", "#20C997"),
        "Hybrid + Rerank": ("#087F5B", "rgba(8, 127, 91, 0.15)", "#20C997"),
    }
    text_color, bg_color, border_color = color_map.get(retrieval_mode, (T['text_muted'], T['surface_alt'], T['border']))

    st.markdown(
        f"<span style='display:inline-block; padding:3px 10px; border-radius:9999px; "
        f"font-size:0.71rem; font-weight:700; background:{bg_color}; color:{text_color}; "
        f"border:1px solid {border_color}; margin-bottom:8px; letter-spacing:0.4px; text-transform:uppercase;'>"
        f"⚡ {retrieval_mode}</span>",
        unsafe_allow_html=True,
    )


def _render_failure_loop_result(loop_result: dict, T: dict = None):
    """
    Render the Phase 4 failure-aware loop result block.
    Shows score summary, original answer (collapsed), and the corrected/refused answer.
    """
    if not loop_result or not loop_result.get("triggered"):
        return

    theme_name = st.session_state.get("theme", "light")
    T = T or THEMES.get(theme_name, THEMES["light"])

    action   = loop_result.get("action", "")
    score    = loop_result.get("score", {})
    reason   = loop_result.get("reason", "")
    original = loop_result.get("original_answer", "")
    final    = loop_result.get("final_answer", "")
    rephrased = loop_result.get("rephrased_query")

    faith = score.get("faithfulness", "?")
    relev = score.get("relevance", "?")

    # Determine faith/relev colors
    faith_color = T['success'] if faith == 1 else T['error']
    relev_color = (
        T['success'] if str(relev).isdigit() and int(relev) >= 2
        else T['warning'] if str(relev).isdigit() and int(relev) == 1
        else T['error']
    )

    alert_bg = "rgba(245, 158, 11, 0.1)" if theme_name == "light" else "rgba(245, 158, 11, 0.18)"
    alert_border = "rgba(245, 158, 11, 0.35)"

    # Correction loop triggered header
    st.markdown(
        f"<div style='background:{alert_bg};border:1px solid {alert_border};border-radius:8px;"
        f"padding:10px 14px;margin:10px 0 6px 0;display:flex;align-items:center;gap:8px;'>"
        f"<span style='font-size:0.74rem;font-weight:700;text-transform:uppercase;"
        f"letter-spacing:0.8px;color:{T['warning']};'>🔁 Correction Loop Triggered</span>"
        f"<span style='font-size:0.72rem;color:{T['text_muted']};'>— {reason}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Score badges
    st.markdown(
        f"<div style='display:flex;gap:6px;align-items:center;margin:6px 0;'>"
        f"<span style='padding:2px 8px;border-radius:4px;background:{faith_color}18;"
        f"color:{faith_color};border:1px solid {faith_color};font-size:0.7rem;font-weight:700;'>"
        f"Faithfulness {faith}/1</span>"
        f"<span style='padding:2px 8px;border-radius:4px;background:{relev_color}18;"
        f"color:{relev_color};border:1px solid {relev_color};font-size:0.7rem;font-weight:700;'>"
        f"Relevance {relev}/3</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Original (low-quality) answer
    with st.expander("📋 Original answer (below threshold)", expanded=False):
        st.markdown(original)

    # Rephrased query
    if action == "rephrased" and rephrased:
        st.markdown(
            f"<div style='font-size:0.76rem; color:{T['text_muted']}; margin:4px 0;'>"
            f"🔄 Rephrased query: <em>{rephrased}</em></div>",
            unsafe_allow_html=True,
        )

    # Action label
    action_labels = {
        "rephrased": ("🔄 Corrected Answer", T['success']),
        "refused":   ("🚫 Refusal (low confidence)", T['error']),
    }
    label, label_color = action_labels.get(action, ("📝 Final Answer", T['text']))
    st.markdown(
        f"<div style='font-size:0.76rem; font-weight:700; color:{label_color}; margin:6px 0 4px;'>"
        f"{label}</div>",
        unsafe_allow_html=True,
    )
