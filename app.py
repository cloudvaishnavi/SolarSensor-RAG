import streamlit as st
import os
import time
from dotenv import load_dotenv

from langchain_community.chat_message_histories import ChatMessageHistory
from PIL import Image

# --------------------------------------------------
# Environment
# --------------------------------------------------
load_dotenv()

from backend.text_utils import img_to_b64, _highlight_answer_phrases

# Phase 2+3+4 UI imports
from ui.components import (
    _render_sources,
    _render_context_chips,
    _render_feedback_widget,
    _render_retrieval_mode_badge,
    _render_failure_loop_result,
)
from ui.sidebar import render_sidebar
from ui.public_landing import render_public_landing
from ui.auth_pages import (
    render_login_page,
    render_signup_page,
    render_forgot_password_page,
)
from ui.pages.knowledge_base_page import render_knowledge_base_page
from ui.pages.upload_page import render_upload_page
from ui.pages.calculator_page import render_calculator_page
from ui.pages.evaluation_page import render_evaluation_page
from ui.pages.settings_page import render_settings_page
from ui.pages.status_page import render_status_page
from ui.pages.questions_page import render_questions_page


# --------------------------------------------------
# Helpers & Assets
# --------------------------------------------------
_base_dir = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(_base_dir, "logo.jpg")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(os.getcwd(), "logo.jpg")

HERO_IMG_PATH = os.path.join(_base_dir, "assets", "rooftop_solar_hero.png")
if not os.path.exists(HERO_IMG_PATH):
    HERO_IMG_PATH = os.path.join(os.getcwd(), "assets", "rooftop_solar_hero.png")

hero_b64 = ""
if os.path.exists(HERO_IMG_PATH):
    import base64
    with open(HERO_IMG_PATH, "rb") as _f:
        hero_b64 = base64.b64encode(_f.read()).decode("utf-8")
logo_b64 = img_to_b64(LOGO_PATH) if os.path.exists(LOGO_PATH) else ""

from backend.vectorstore import create_vector_store, _parse_retry_delay, DOCS_FOLDER
from backend.chains import _call_direct_llm, build_qa_chain

os.makedirs(DOCS_FOLDER, exist_ok=True)

# --------------------------------------------------
# Page Config
# --------------------------------------------------
page_icon_img = Image.open(LOGO_PATH) if os.path.exists(LOGO_PATH) else "☀️"

st.set_page_config(
    page_title="SolarSense — Rooftop Solar AI Assistant",
    page_icon=page_icon_img,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# THEME SYSTEM
# --------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

from ui.theme import THEMES, get_css
T = THEMES[st.session_state.theme]

_css = get_css(st.session_state.theme)
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

# --------------------------------------------------
# Public & Auth Page Routing
# --------------------------------------------------
_PUBLIC_PAGES = {"landing", "login", "signup", "forgot_password"}
_VALID_DASHBOARD_PAGES = [
    "Chat Assistant",
    "Knowledge Base",
    "Upload Documents",
    "Solar Calculator",
    "Evaluation & Results",
    "Settings & Advanced Retrieval",
    "System Status & Architecture",
    "Example Questions",
]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"

# Check query params for deep-link / direct page routing
if "page" in st.query_params:
    qp = st.query_params["page"].strip()
    qp_lower = qp.lower()
    if qp_lower in ("dashboard", "app", "demo"):
        st.session_state["authenticated"] = True
        st.session_state["preview_mode"] = True
        st.session_state["user_name"] = "Demo Visitor"
        st.session_state.current_page = "Chat Assistant"
        st.session_state["_last_query_page"] = "dashboard"
        try:
            st.query_params.clear()
        except Exception:
            pass
    elif st.session_state.get("_last_query_page") != qp:
        st.session_state["_last_query_page"] = qp
        if qp_lower in ("landing", "home"):
            st.session_state.current_page = "landing"
        elif qp_lower == "login":
            if st.session_state.get("authenticated") or st.session_state.get("preview_mode"):
                st.session_state.current_page = "Chat Assistant"
                try:
                    st.query_params.clear()
                except Exception:
                    pass
            else:
                st.session_state.current_page = "login"
        elif qp_lower in ("signup", "register"):
            if st.session_state.get("authenticated") or st.session_state.get("preview_mode"):
                st.session_state.current_page = "Chat Assistant"
                try:
                    st.query_params.clear()
                except Exception:
                    pass
            else:
                st.session_state.current_page = "signup"
        elif qp_lower in ("forgot", "forgot_password"):
            st.session_state.current_page = "forgot_password"
        elif qp in _VALID_DASHBOARD_PAGES:
            st.session_state["authenticated"] = True
            st.session_state["preview_mode"] = True
            st.session_state["user_name"] = "Demo Visitor"
            st.session_state.current_page = qp

# Access Guard: Unauthenticated visitors cannot access dashboard pages directly
if st.session_state.current_page in _VALID_DASHBOARD_PAGES:
    if not (st.session_state.get("authenticated") or st.session_state.get("preview_mode")):
        st.session_state.current_page = "landing"

# If current page is a public page, render it and stop before loading vectorstore / dashboard chrome
if st.session_state.current_page in _PUBLIC_PAGES:
    if st.session_state.current_page == "landing":
        render_public_landing(T)
    elif st.session_state.current_page == "login":
        render_login_page(T)
    elif st.session_state.current_page == "signup":
        render_signup_page(T)
    elif st.session_state.current_page == "forgot_password":
        render_forgot_password_page(T)
    st.stop()

# --------------------------------------------------
# Load knowledge base
# --------------------------------------------------
if "kb_loaded" not in st.session_state:
    st.session_state.kb_loaded = False

if not st.session_state.kb_loaded:
    with st.spinner("Loading SolarSense knowledge base…"):
        vectorstore, doc_count, doc_names = create_vector_store()
    st.session_state.kb_loaded = True
else:
    vectorstore, doc_count, doc_names = create_vector_store()

# --------------------------------------------------
# Left Navigation Sidebar
# --------------------------------------------------
render_sidebar(vectorstore, doc_count, doc_names, T, LOGO_PATH)

# --------------------------------------------------
# --------------------------------------------------
# Stitch Top Bar Navigation
# --------------------------------------------------
kb_live = vectorstore is not None

with st.container(key="stitch_top_nav"):
    brand_col, ctrl_col = st.columns([7.8, 4.2])
    with brand_col:
        top_logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" class="top-nav-logo-img" alt="SolarSense Logo" />' if logo_b64 else '<div class="top-nav-logo-fallback">☀️</div>'
        st.markdown(
            f'''<div class="top-nav-brand-wrap">
                {top_logo_html}
                <span class="top-nav-brand-title">SOLAR SENSE</span>
            </div>''',
            unsafe_allow_html=True,
        )
    with ctrl_col:
        with st.container(key="stitch_header_cluster"):
            c_avatar, c_theme, c_logout = st.columns([1.35, 1, 1], gap="small")
            with c_avatar:
                user_name = st.session_state.get("user_name", "")
                is_preview = st.session_state.get("preview_mode", False)
                avatar_char = user_name.strip()[0].upper() if user_name.strip() else ("D" if is_preview else "U")
                display_name = user_name if user_name else ("Demo Visitor" if is_preview else "SolarSense User")
                role_label = "Demo" if is_preview else "Active"
                user_title = f"{display_name} • {role_label} Mode"
                st.markdown(
                    f'''<div class="user-profile-chip" title="{user_title}"><div class="user-avatar-badge"><span>{avatar_char}</span><span class="user-status-dot"></span></div><div class="user-chip-text"><span class="user-chip-role">{role_label}</span></div></div>''',
                    unsafe_allow_html=True,
                )
            with c_theme:
                toggle_icon_main = "☀️" if st.session_state.theme == "dark" else "🌙"
                toggle_help = "Switch to Light mode" if st.session_state.theme == "dark" else "Switch to Dark mode"
                if st.button(toggle_icon_main, key="theme_toggle_main", help=toggle_help):
                    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                    st.rerun()
            with c_logout:
                logout_help = "Exit Demo / Return to Home" if is_preview else "Sign Out to Home"
                if st.button("🚪", key="top_sign_out_btn", help=logout_help):
                    from ui.auth_service import sign_out
                    sign_out()
                    st.rerun()

# --------------------------------------------------
# QA Chain with Conversational Memory
# --------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

if "latest_sources" not in st.session_state:
    st.session_state.latest_sources = []

qa_chain, retriever_ref = build_qa_chain(vectorstore)

# Chat Messages & Compare Mode
if "messages" not in st.session_state:
    st.session_state.messages = []

if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False

if "retrieval_mode" not in st.session_state:
    st.session_state.retrieval_mode = "Dense only"

if "chunk_size" not in st.session_state:
    st.session_state.chunk_size = 900

if "chunk_overlap" not in st.session_state:
    st.session_state.chunk_overlap = 180

if "rerank_top_k" not in st.session_state:
    st.session_state.rerank_top_k = 5

if "hybrid_alpha" not in st.session_state:
    st.session_state.hybrid_alpha = 0.7

# --------------------------------------------------
# Dashboard Page Routing
# --------------------------------------------------
if st.session_state.current_page == "Knowledge Base":
    render_knowledge_base_page(vectorstore, doc_count, doc_names, T)
    st.stop()
elif st.session_state.current_page == "Upload Documents":
    render_upload_page(vectorstore, doc_count, doc_names, T)
    st.stop()
elif st.session_state.current_page == "Solar Calculator":
    render_calculator_page(T)
    st.stop()
elif st.session_state.current_page == "Evaluation & Results":
    render_evaluation_page(T)
    st.stop()
elif st.session_state.current_page == "Settings & Advanced Retrieval":
    render_settings_page(vectorstore, T)
    st.stop()
elif st.session_state.current_page == "System Status & Architecture":
    render_status_page(vectorstore, doc_count, doc_names, T)
    st.stop()
elif st.session_state.current_page == "Example Questions":
    render_questions_page(T)
    st.stop()

# --------------------------------------------------
# 2-Column Responsive Layout: Center Workspace + Right Rail
# --------------------------------------------------
center_col, right_col = st.columns([7, 3], gap="large")

with center_col:
    # --------------------------------------------------
    # 1. Stitch Rooftop Solar Hero Banner with Real Photo
    # --------------------------------------------------
    hero_img_html = f'<img src="data:image/png;base64,{hero_b64}" alt="Rooftop Solar Installation"/>' if hero_b64 else ''
    st.html(
        f"""
<div class="stitch-hero">
    <div class="stitch-hero-bg-img">
        {hero_img_html}
        <div class="stitch-hero-overlay"></div>
    </div>
    <div class="stitch-hero-content">
        <div class="hero-pill">
            <span>🌱</span>
            <span>AI-Powered</span>
        </div>
        <h1 class="hero-title">SolarSense</h1>
        <div class="hero-sub">Your trusted AI assistant for rooftop solar</div>
        <p class="hero-desc">
            Get accurate, up-to-date answers about PM Surya Ghar, solar systems, battery storage,
            costs, subsidies and more &mdash; grounded in reliable sources.
        </p>
        <div class="hero-chips-row">
            <span class="hero-chip"><span style="color:#20C997;font-weight:700;">✓</span> Reliable Information</span>
            <span class="hero-chip"><span style="color:#087F5B;">📄</span> Source-backed Answers</span>
            <span class="hero-chip"><span style="color:#087F5B;">⚡</span> Latest Guidelines</span>
            <span class="hero-chip"><span style="color:#20C997;">🌱</span> Supports Your Solar Journey</span>
        </div>
    </div>
</div>
"""
    )

    # --------------------------------------------------
    # 2. Six Interactive Suggested Question Cards
    # --------------------------------------------------
    if len(st.session_state.messages) == 0:
        st.markdown(
            """
<div class="prompt-grid-header">
    <span>👋</span> How can I help you today?
</div>
<div class="prompt-grid-sub">
    Ask anything about rooftop solar, PM Surya Ghar, subsidies, battery sizing, installation, or upload your documents.
</div>
""",
            unsafe_allow_html=True,
        )

        starters = [
            ("📄", "What is PM Surya Ghar?", "Learn about the scheme and benefits", "What is the PM Surya Ghar scheme and how do I apply?"),
            ("👤", "Am I eligible for subsidy?", "Check eligibility criteria", "Am I eligible for the PM Surya Ghar rooftop solar subsidy?"),
            ("📊", "How much can I save?", "Estimate cost savings", "How much money and electricity bill can I save with rooftop solar?"),
            ("🔋", "What size battery do I need?", "Get battery recommendations", "What size battery storage do I need for rooftop solar?"),
            ("🔄", "How does net metering work?", "Understand the process", "How does net metering work for residential rooftop solar in India?"),
            ("📖", "Show latest guidelines", "Get policy updates", "What are the latest MNRE guidelines for rooftop solar installations?"),
        ]

        with st.container(key="starter_card_container"):
            row1_cols = st.columns(3)
            for idx in range(3):
                icon, title, desc, query = starters[idx]
                with row1_cols[idx]:
                    if st.button(f"{icon}  **{title}**\n\n{desc}", key=f"starter_btn_{idx}", use_container_width=True):
                        st.session_state["pending_prompt"] = query
                        st.rerun()

            row2_cols = st.columns(3)
            for idx in range(3, 6):
                icon, title, desc, query = starters[idx]
                with row2_cols[idx - 3]:
                    if st.button(f"{icon}  **{title}**\n\n{desc}", key=f"starter_btn_{idx}", use_container_width=True):
                        st.session_state["pending_prompt"] = query
                        st.rerun()

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # --------------------------------------------------
    # 3. Compare Mode Toggle Card
    # --------------------------------------------------
    _cmp_on = st.session_state.compare_mode
    _badge_color = "#087F5B" if _cmp_on else "#64756B"
    _badge_bg = "#D4E5D8" if _cmp_on else "#E9F2EA"
    _badge_label = "ACTIVE" if _cmp_on else "OFF"
    _desc = (
        "Side-by-side grounded vs. ungrounded direct LLM responses shown for each turn."
        if _cmp_on else
        "Only the grounded RAG answer is shown (recommended for reliable domain guidance)."
    )

    st.markdown(
        f"""
<div class="compare-mode-card">
    <div style="display:flex;align-items:center;gap:12px;">
        <span style="font-size:1.35rem;">🔍</span>
        <div>
            <div style="font-size:0.88rem;font-weight:800;color:#052E24;display:flex;align-items:center;gap:8px;">
                Compare: RAG vs Direct LLM
                <span style="background:{_badge_bg};color:{_badge_color};padding:2px 8px;border-radius:9999px;font-size:0.68rem;font-weight:700;border:1px solid {_badge_color};">{_badge_label}</span>
            </div>
            <div style="font-size:0.75rem;color:#64756B;margin-top:2px;font-weight:500;">{_desc}</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    _new_compare = st.toggle(
        "Toggle RAG vs Direct LLM Comparison",
        value=_cmp_on,
        key="_compare_toggle_widget",
        help="When ON, answers include a direct comparison showing what the model produces without access to your documents.",
    )
    if _new_compare != _cmp_on:
        st.session_state.compare_mode = _new_compare
        st.rerun()

    # --------------------------------------------------
    # 4. Chat Messages History Stream
    # --------------------------------------------------
    user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
    asst_idx = 0
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant":
                _render_context_chips(msg.get("sources", []), msg["content"])
                _sources = msg.get("sources", [])
                _annotated = _highlight_answer_phrases(msg["content"], _sources)
                st.markdown(_annotated, unsafe_allow_html=bool(_sources))
                _render_sources(_sources, msg["content"])

                if msg.get("direct_answer"):
                    with st.expander("🔍 RAG vs Direct LLM Side-by-Side Comparison", expanded=True):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"""
                            <div class="compare-card compare-card-rag">
                                <div class="compare-card-label compare-card-label-rag">✅ Grounded (RAG)</div>
                                {msg["content"]}
                            </div>""", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"""
                            <div class="compare-card compare-card-direct">
                                <div class="compare-card-label compare-card-label-direct">⚠️ Ungrounded (Direct)</div>
                                {msg["direct_answer"]}
                            </div>
                            <div class="compare-warning">ℹ️ The direct answer uses general model knowledge without your documents. It may be incomplete or inaccurate. Always prefer the Grounded (RAG) answer.</div>
                            """, unsafe_allow_html=True)

                rewritten = msg.get("rewritten_query", "")
                if rewritten and rewritten != msg.get("original_question", rewritten):
                    with st.expander("🔎 Standalone Reformulated Retrieval Query", expanded=False):
                        st.code(rewritten, language=None)

                loop_res = msg.get("loop_result")
                if loop_res and loop_res.get("triggered"):
                    _render_failure_loop_result(loop_res, T)

                q_for_fb = user_msgs[asst_idx]["content"] if asst_idx < len(user_msgs) else ""
                _render_feedback_widget(asst_idx, q_for_fb, msg["content"])
                asst_idx += 1
            else:
                st.markdown(msg["content"])


with right_col:
    # --------------------------------------------------
    # Right Information Panel: Real-time KB Status & Stats
    # --------------------------------------------------
    _display_chunk = st.session_state.get("chunk_size", 900)
    _display_overlap = st.session_state.get("chunk_overlap", 180)
    retrieval_mode_display = st.session_state.get("retrieval_mode", "Dense only")

    kb_status_title = "Knowledge Base Ready" if kb_live else "Knowledge Base Offline"
    kb_status_sub = f"{doc_count} documents indexed" if kb_live else "Upload documents to begin"

    # 1. Knowledge Base Ready Card
    st.markdown(
        f"""
<div class="kb-status-card">
    <div style="display:flex;align-items:center;gap:12px;">
        <span class="beacon-dot" style="background:{'#20C997' if kb_live else '#94A3B8'};box-shadow:0 0 0 3px {'rgba(32,201,151,0.32)' if kb_live else 'rgba(148,163,184,0.2)'};"></span>
        <div>
            <div class="kb-status-title">{kb_status_title}</div>
            <div class="kb-status-sub">{kb_status_sub}</div>
        </div>
    </div>
    <div class="kb-status-icon-wrap">🗄️</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # 2. Quick Stats 2x2 Grid
    st.markdown(
        f"""
<div class="quick-stats-card">
    <div class="quick-stats-title">Quick Stats</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div class="quick-stat-box">
            <div style="width:30px;height:30px;border-radius:8px;background:{T['blue_soft']};color:{T['blue']};display:flex;align-items:center;justify-content:center;font-size:0.95rem;flex-shrink:0;">📄</div>
            <div>
                <div class="quick-stat-val">{doc_count}</div>
                <div class="quick-stat-lbl">Documents</div>
            </div>
        </div>
        <div class="quick-stat-box">
            <div style="width:30px;height:30px;border-radius:8px;background:{T['accent_soft']};color:{T['accent']};display:flex;align-items:center;justify-content:center;font-size:0.95rem;flex-shrink:0;">📏</div>
            <div>
                <div class="quick-stat-val">{_display_chunk}</div>
                <div class="quick-stat-lbl">Chunk Size</div>
            </div>
        </div>
        <div class="quick-stat-box">
            <div style="width:30px;height:30px;border-radius:8px;background:{T['warning_soft']};color:{T['warning']};display:flex;align-items:center;justify-content:center;font-size:0.95rem;flex-shrink:0;">⚙️</div>
            <div>
                <div class="quick-stat-val" style="font-size:0.75rem;">{retrieval_mode_display}</div>
                <div class="quick-stat-lbl">Retrieval</div>
            </div>
        </div>
        <div class="quick-stat-box">
            <div style="width:30px;height:30px;border-radius:8px;background:{T['success_soft']};color:{T['success']};display:flex;align-items:center;justify-content:center;font-size:0.95rem;flex-shrink:0;">
                <span style="width:8px;height:8px;border-radius:50%;background:{T['success']};display:inline-block;"></span>
            </div>
            <div>
                <div class="quick-stat-val" style="color:{T['success']};">{'Live' if kb_live else 'Offline'}</div>
                <div class="quick-stat-lbl">FAISS Index</div>
            </div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # 3. Suggested Questions List
    with st.container(key="suggested_rail_box"):
        st.markdown(
            """
<div class="suggested-rail-header">
    <div class="suggested-rail-title">
        <span style="color:#F59E0B;">💡</span>
        <span>Suggested Questions</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )
        suggested_rail = [
            ("How much subsidy is available?  ›", "How much subsidy is available under PM Surya Ghar?"),
            ("Explain net metering  ›", "Explain net metering policies and billing guidelines for rooftop solar."),
            ("What is Cost-Save mode?  ›", "What is Cost-Save mode for rooftop solar battery systems?"),
            ("How does monsoon pre-charge work?  ›", "How does monsoon pre-charge work for solar batteries?"),
            ("What are the latest guidelines?  ›", "What are the latest PM Surya Ghar operational guidelines?"),
        ]

        for label, query in suggested_rail:
            if st.button(label, key=f"rail_q_{label}", use_container_width=True):
                st.session_state["pending_prompt"] = query
                st.rerun()

    # 4. Clean Energy Card (Elegant grey-green design without black SVG)
    st.markdown(
        """
<div class="eco-artwork-card">
    <div class="eco-artwork-content">
        <div class="eco-artwork-icon">🌱</div>
        <div>
            <div class="eco-artwork-title">Clean Energy</div>
            <div class="eco-artwork-sub">Brighter Future for India</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# Chat Input Handling & RAG Invocation
# --------------------------------------------------
prompt = None
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")
user_input = st.chat_input("Type your question here...")
if user_input:
    prompt = user_input

if prompt:
    if qa_chain is None:
        st.warning("⚠️ Knowledge base is offline. Please upload solar policy documents via the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            retrieval_mode = st.session_state.get("retrieval_mode", "Dense only")
            rerank_top_k = st.session_state.get("rerank_top_k", 5)
            hybrid_alpha = st.session_state.get("hybrid_alpha", 0.7)
            failure_loop_on = st.session_state.get("failure_loop_enabled", False)
            fail_faith_thr = st.session_state.get("fail_faith_threshold", 1)
            fail_relev_thr = st.session_state.get("fail_relev_threshold", 2)
            fail_loop_action = st.session_state.get("fail_loop_action", "rephrase")

            with st.spinner("🔍 Retrieving knowledge & generating grounded response…"):
                st.session_state.latest_sources = []
                st.session_state["_last_rewritten_query"] = prompt
                success = False
                answer = ""
                sources = []
                retrieved_context = ""

                # PATH A: Dense-only (original, untouched qa_chain path)
                if retrieval_mode == "Dense only":
                    for attempt in range(3):
                        try:
                            answer = qa_chain.invoke(
                                {"question": prompt},
                                config={"configurable": {"session_id": "default"}},
                            )
                            success = True
                            break
                        except Exception as e:
                            err_str = str(e)
                            if "500" in err_str or "503" in err_str or "INTERNAL" in err_str or "Quota" in err_str or "429" in err_str:
                                if attempt < 2:
                                    wait = _parse_retry_delay(err_str, default=5 * (attempt + 1))
                                    time.sleep(wait)
                                    continue
                            friendly_msg = "Google API is temporarily rate-limited. Please wait 20-30 seconds and try again."
                            if "404" in err_str or "not found" in err_str.lower():
                                friendly_msg = "Model configuration error. Please ensure the model name is correct."
                            st.error(f"❌ {friendly_msg}\n\n*(Technical details: {err_str[:120]}...)*")
                            break

                    if success:
                        sources = st.session_state.latest_sources
                        if sources:
                            from backend.retrieval_pipeline import format_docs_for_context
                            retrieved_context = format_docs_for_context(sources)

                # PATH B: Dense+Rerank or Hybrid+Rerank
                else:
                    try:
                        from backend.retrieval_pipeline import retrieve, format_docs_for_context
                        from backend.vectorstore import LLM_MODEL
                        from langchain_google_genai import ChatGoogleGenerativeAI
                        from langchain_core.prompts import ChatPromptTemplate
                        from langchain_core.output_parsers import StrOutputParser

                        pipeline_docs = retrieve(
                            query=prompt,
                            vectorstore=vectorstore,
                            retrieval_mode=retrieval_mode,
                            reranker_enabled=True,
                            rerank_top_k=rerank_top_k,
                            hybrid_alpha=hybrid_alpha,
                        )
                        retrieved_context = format_docs_for_context(pipeline_docs)
                        st.session_state.latest_sources = pipeline_docs

                        _GEN_SYS = """You are SolarSense, an expert AI assistant specialising in Indian rooftop solar systems and the PM Surya Ghar (MNRE) scheme.

**STRICT GROUNDING RULES (MUST FOLLOW):**
- You MUST answer the user's question ONLY using the context provided below.
- If the context does not contain the answer, you MUST reply EXACTLY with:
  "I don't have enough information in the loaded documents to answer that accurately. Please upload the relevant document or rephrase your question."
- Do NOT use outside knowledge. Do NOT speculate, guess, or invent answers.

**ANSWER QUALITY RULES:**
- Open with a direct answer to the question in the first sentence.
- Synthesize the context in your own words rather than copy-pasting it verbatim.
- Use bullet points only when the answer genuinely has multiple distinct parts.
- When discussing PM Surya Ghar subsidies, state the official slab clearly.
- Cite the source document naturally when providing factual information.

Context from loaded documents:
{context}"""

                        _gen_llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.15)
                        _gen_prompt = ChatPromptTemplate.from_messages([
                            ("system", _GEN_SYS),
                            ("human", "{question}"),
                        ])
                        _gen_chain = _gen_prompt | _gen_llm | StrOutputParser()

                        for attempt in range(3):
                            try:
                                answer = _gen_chain.invoke({"question": prompt, "context": retrieved_context})
                                success = True
                                break
                            except Exception as e:
                                err_str = str(e)
                                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "500" in err_str or "503" in err_str:
                                    if attempt < 2:
                                        wait = _parse_retry_delay(err_str, default=5 * (attempt + 1))
                                        time.sleep(wait)
                                        continue
                                friendly_msg = "Google API is temporarily rate-limited. Please wait 20-30 seconds and try again."
                                if "404" in err_str or "not found" in err_str.lower():
                                    friendly_msg = "Model configuration error."
                                st.error(f"❌ {friendly_msg}\n\n*(Technical details: {err_str[:120]}...)*")
                                break

                        sources = st.session_state.latest_sources

                    except Exception as e:
                        st.error(f"❌ Retrieval pipeline error: {str(e)[:180]}")

            # ---------------------------------------------------------------
            # Render answer
            # ---------------------------------------------------------------
            if success:
                rewritten_query = st.session_state.get("_last_rewritten_query", prompt)
                direct_answer = ""

                _render_retrieval_mode_badge(retrieval_mode, T)
                _render_context_chips(sources, answer)
                _annotated_answer = _highlight_answer_phrases(answer, sources)
                st.markdown(_annotated_answer, unsafe_allow_html=bool(sources))
                _render_sources(sources, answer)

                # Phase 4: Failure-Aware Loop
                loop_result = None
                if failure_loop_on and retrieved_context and answer:
                    with st.spinner("🔁 Running quality check…"):
                        try:
                            from backend.failure_loop import run_failure_loop
                            from backend.vectorstore import LLM_MODEL
                            from langchain_google_genai import ChatGoogleGenerativeAI
                            from langchain_core.prompts import ChatPromptTemplate
                            from langchain_core.output_parsers import StrOutputParser

                            _judge_llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.0)
                            _judge_prompt = ChatPromptTemplate.from_messages([("human", "{text}")])
                            _judge_chain = _judge_prompt | _judge_llm | StrOutputParser()
                            _llm_callable = lambda p: _judge_chain.invoke({"text": p})

                            def _gen_callable(q, ctx):
                                from langchain_google_genai import ChatGoogleGenerativeAI
                                from langchain_core.prompts import ChatPromptTemplate
                                from langchain_core.output_parsers import StrOutputParser
                                _llm2 = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.15)
                                _p2 = ChatPromptTemplate.from_messages([
                                    ("system", "Answer using ONLY the provided context.\n\nContext:\n{context}"),
                                    ("human", "{question}"),
                                ])
                                return (_p2 | _llm2 | StrOutputParser()).invoke({"question": q, "context": ctx})

                            loop_result = run_failure_loop(
                                question=prompt,
                                answer=answer,
                                context=retrieved_context,
                                docs=sources,
                                vectorstore=vectorstore,
                                llm_callable=_llm_callable,
                                gen_callable=_gen_callable,
                                config={
                                    "faith_threshold": fail_faith_thr,
                                    "relev_threshold": fail_relev_thr,
                                    "loop_action": fail_loop_action,
                                    "retrieval_mode": retrieval_mode,
                                    "reranker_enabled": retrieval_mode != "Dense only",
                                    "rerank_top_k": rerank_top_k,
                                    "hybrid_alpha": hybrid_alpha,
                                },
                            )
                            if loop_result and loop_result.get("triggered"):
                                _render_failure_loop_result(loop_result, T)
                                st.markdown(loop_result["final_answer"])
                                answer = loop_result["final_answer"]
                        except Exception as loop_err:
                            st.caption(f"⚠️ Quality check failed: {str(loop_err)[:100]}")

                # Feature 4: RAG vs Direct comparison
                if st.session_state.compare_mode:
                    with st.spinner("Running direct (no-retrieval) LLM call for comparison…"):
                        direct_answer = _call_direct_llm(prompt)
                    with st.expander("🔍 RAG vs Direct LLM Side-by-Side Comparison", expanded=True):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"""
                            <div class="compare-card compare-card-rag">
                                <div class="compare-card-label compare-card-label-rag">✅ Grounded (RAG)</div>
                                {answer}
                            </div>""", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"""
                            <div class="compare-card compare-card-direct">
                                <div class="compare-card-label compare-card-label-direct">⚠️ Ungrounded (Direct)</div>
                                {direct_answer}
                            </div>
                            <div class="compare-warning">ℹ️ The direct answer uses general model knowledge without your documents. It may be incomplete or inaccurate. Always prefer the Grounded (RAG) answer.</div>
                            """, unsafe_allow_html=True)

                # Feature 6: Rewritten query debug
                if rewritten_query and rewritten_query != prompt:
                    with st.expander("🔎 Standalone Reformulated Retrieval Query", expanded=False):
                        st.code(rewritten_query, language=None)

                # Feature 1: Feedback widget
                msg_index = len([m for m in st.session_state.messages if m["role"] == "assistant"])
                _render_feedback_widget(msg_index, prompt, answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "direct_answer": direct_answer,
                    "rewritten_query": rewritten_query,
                    "original_question": prompt,
                    "retrieval_mode": retrieval_mode,
                    "loop_result": loop_result,
                })
                st.rerun()

# --------------------------------------------------
# Evaluation & Results is now rendered on its dedicated page (ui/pages/evaluation_page.py)
# --------------------------------------------------