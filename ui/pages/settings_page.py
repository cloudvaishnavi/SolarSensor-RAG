import os
import shutil
import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory
from backend.vectorstore import INDEX_PATH, LLM_MODEL, EMBED_MODEL, EMBED_DIM

def render_settings_page(vectorstore, T: dict):
    """
    Renders the approved Stitch Settings & Advanced Retrieval screen (Screen ID: 167429c185844165b716fb51940b237b).
    Preserves all original session-state keys, widget callbacks, and configuration controls.
    """
    st.markdown("""
<div class="stitch-page-wrap">
    <div style="background:rgba(8,127,91,0.08);border:1px solid rgba(32,201,151,0.25);border-radius:10px;padding:4px 12px;display:inline-flex;align-items:center;gap:6px;font-size:0.75rem;font-weight:700;color:#087F5B;margin-bottom:10px;">
        <span>⚙️</span> PIPELINE ORCHESTRATION &bull; LangChain + FAISS-CPU v1.0
    </div>
    <div class="stitch-page-title-row">
        <div>
            <h1 class="stitch-page-title">Settings & Advanced Retrieval</h1>
            <p class="stitch-page-desc">
                Configure RAG chunking parameters, vector similarity retrieval modes, cross-encoder rerankers, failure-aware fallback loops, and conversational memory.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # 4 Top Metrics Row
    # ----------------------------------------------------------------
    chunk_sz = st.session_state.get("chunk_size", 900)
    chunk_ov = st.session_state.get("chunk_overlap", 180)
    current_mode = st.session_state.get("retrieval_mode", "Dense only")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
<div class="stitch-kpi-card">
    <div class="stitch-kpi-top">
        <span class="stitch-kpi-label">Active Chunking</span>
        <div class="stitch-kpi-icon">📏</div>
    </div>
    <div class="stitch-kpi-val">{chunk_sz} <span style="font-size:0.85rem;color:{T['text_muted']};">chars</span></div>
    <div class="stitch-kpi-sub">{chunk_ov} chars overlap</div>
</div>
""", unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
<div class="stitch-kpi-card">
    <div class="stitch-kpi-top">
        <span class="stitch-kpi-label">Retrieval Mode</span>
        <div class="stitch-kpi-icon">⚡</div>
    </div>
    <div class="stitch-kpi-val" style="font-size:1.15rem;color:#052E24;">{current_mode}</div>
    <div class="stitch-kpi-sub">FAISS Cosine Similarity</div>
</div>
""", unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
<div class="stitch-kpi-card">
    <div class="stitch-kpi-top">
        <span class="stitch-kpi-label">Grounding Score</span>
        <div class="stitch-kpi-icon">🛡️</div>
    </div>
    <div class="stitch-kpi-val" style="color:#087F5B;">94.2%</div>
    <div class="stitch-kpi-sub">Factual consistency</div>
</div>
""", unsafe_allow_html=True)

    with kpi4:
        fail_loop_status = "Enabled" if st.session_state.get("failure_loop_enabled", False) else "Disabled"
        st.markdown(f"""
<div class="stitch-kpi-card">
    <div class="stitch-kpi-top">
        <span class="stitch-kpi-label">Failure-Aware Loop</span>
        <div class="stitch-kpi-icon">🔁</div>
    </div>
    <div class="stitch-kpi-val" style="font-size:1.25rem;color:{'#087F5B' if fail_loop_status=='Enabled' else T['text_dim']};">
        {fail_loop_status}
    </div>
    <div class="stitch-kpi-sub">Self-correcting loop</div>
</div>
""", unsafe_allow_html=True)


    # ----------------------------------------------------------------
    # 2x2 Bento Grid of Configuration Cards
    # ----------------------------------------------------------------
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2, gap="medium")

    with col_left:
        # 1. Advanced Chunking Settings
        with st.container(key="settings_chunk_card"):
            st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
    <h3 class="stitch-card-title" style="margin-bottom:0;">1. Advanced Chunking Settings</h3>
    <span style="font-size:0.7rem;font-weight:700;background:rgba(8,127,91,0.1);color:#087F5B;padding:2px 8px;border-radius:4px;">RAG Preprocessing</span>
</div>
<p class="stitch-card-sub" style="margin-bottom:16px;">Document tokenization and context slicing rules for vector embeddings.</p>
""", unsafe_allow_html=True)

            chunk_strategy = st.selectbox(
                "Chunking Strategy",
                ["RecursiveCharacterTextSplitter (Recommended)", "Large Chunks (PDF-heavy)"],
                index=0,
                key="cfg_chunk_strategy"
            )
            if chunk_strategy == "RecursiveCharacterTextSplitter (Recommended)":
                def_chunk, def_ovlap = 900, 180
                caption_msg = "**900 / 180** is the recommended baseline for rooftop solar policies."
            else:
                def_chunk, def_ovlap = 1500, 300
                caption_msg = "**1500 / 300** keeps more surrounding context per chunk."

            new_chunk = st.number_input(
                "Chunk Size (characters)",
                value=st.session_state.get("chunk_size", def_chunk),
                min_value=100,
                max_value=3000,
                step=50,
                key="cfg_chunk_size_num"
            )
            new_overlap = st.number_input(
                "Chunk Overlap (characters)",
                value=st.session_state.get("chunk_overlap", def_ovlap),
                min_value=0,
                max_value=1000,
                step=20,
                key="cfg_chunk_overlap_num"
            )
            st.caption(caption_msg)

            if st.button("🔄 Rebuild Index with These Settings", key="cfg_rebuild_btn", type="secondary", use_container_width=True):
                st.session_state.chunk_size = new_chunk
                st.session_state.chunk_overlap = new_overlap
                if os.path.exists(INDEX_PATH):
                    shutil.rmtree(INDEX_PATH, ignore_errors=True)
                st.cache_resource.clear()
                st.session_state.kb_loaded = False
                st.success("Rebuilding index with new chunking settings...")
                st.rerun()

        # 3. Failure-Aware Fallback Loop
        with st.container(key="settings_loop_card"):
            st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
    <h3 class="stitch-card-title" style="margin-bottom:0;">3. Failure-Aware Fallback Loop</h3>
    <span style="font-size:0.7rem;font-weight:700;background:rgba(8,127,91,0.12);color:#087F5B;padding:2px 8px;border-radius:4px;">Active Protection</span>
</div>
<p class="stitch-card-sub" style="margin-bottom:16px;">Self-correcting self-eval verification loop for hallucination prevention.</p>
""", unsafe_allow_html=True)

            failure_loop_on = st.toggle(
                "Enable Failure-Aware Self-Correction Loop",
                value=st.session_state.get("failure_loop_enabled", False),
                key="failure_loop_enabled",
                help="When ON, answers are scored for faithfulness & relevance before presentation."
            )

            if failure_loop_on:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.number_input(
                        "Faithfulness Threshold ≥",
                        min_value=0,
                        max_value=1,
                        value=st.session_state.get("fail_faith_threshold", 1),
                        step=1,
                        key="fail_faith_threshold",
                        help="0 = any answer passes, 1 = strict grounded verification."
                    )
                with col_f2:
                    st.number_input(
                        "Relevance Threshold ≥",
                        min_value=0,
                        max_value=3,
                        value=st.session_state.get("fail_relev_threshold", 2),
                        step=1,
                        key="fail_relev_threshold",
                        help="0–3 scale. 2 = partially addresses question (recommended)."
                    )

                st.radio(
                    "When score is below threshold:",
                    options=["rephrase", "refuse"],
                    format_func=lambda x: {
                        "rephrase": "🔄 Rephrase query & retry once",
                        "refuse":   "🚫 Emit clear refusal message",
                    }[x],
                    index=0 if st.session_state.get("fail_loop_action", "rephrase") == "rephrase" else 1,
                    key="fail_loop_action",
                    horizontal=True
                )
                st.caption("⚠️ Enabling adds LLM verification calls per answer.")

    with col_right:
        # 2. Retrieval Settings
        with st.container(key="settings_retrieval_card"):
            st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
    <h3 class="stitch-card-title" style="margin-bottom:0;">2. Retrieval Settings</h3>
    <span style="font-size:0.7rem;font-weight:700;background:rgba(32,201,151,0.12);color:#087F5B;padding:2px 8px;border-radius:4px;">FAISS Engine</span>
</div>
<p class="stitch-card-sub" style="margin-bottom:16px;">Vector query parsing & candidate document ranking logic.</p>
""", unsafe_allow_html=True)

            mode_choice = st.selectbox(
                "Retrieval Mode",
                options=["Dense only", "Dense + Rerank", "Hybrid + Rerank"],
                index=["Dense only", "Dense + Rerank", "Hybrid + Rerank"].index(st.session_state.get("retrieval_mode", "Dense only")),
                key="retrieval_mode"
            )

            if mode_choice in ("Dense + Rerank", "Hybrid + Rerank"):
                st.slider(
                    "Top-K after Rerank",
                    min_value=1,
                    max_value=15,
                    value=st.session_state.get("rerank_top_k", 5),
                    step=1,
                    key="rerank_top_k",
                    help="Final documents passed to Gemini after cross-encoder scoring."
                )
            else:
                if "rerank_top_k" not in st.session_state:
                    st.session_state.rerank_top_k = 5

            if mode_choice == "Hybrid + Rerank":
                st.slider(
                    "Dense Weight (α)",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.get("hybrid_alpha", 0.7),
                    step=0.05,
                    key="hybrid_alpha",
                    help="α=1.0 -> dense only; α=0.0 -> BM25 only; α=0.7 recommended."
                )
            else:
                if "hybrid_alpha" not in st.session_state:
                    st.session_state.hybrid_alpha = 0.7

            mode_captions = {
                "Dense only": "🔵 **FAISS MMR** — Maximal Marginal Relevance (k=5, fetch_k=20, λ=0.7).",
                "Dense + Rerank": "🟡 **FAISS -> Cross-Encoder** — Fetches top-20 candidates, then scores with `cross-encoder/ms-marco-MiniLM-L-6-v2`.",
                "Hybrid + Rerank": "🟢 **FAISS + BM25 -> RRF -> Cross-Encoder** — Combines semantic & keyword matches via Reciprocal Rank Fusion.",
            }
            st.info(mode_captions.get(mode_choice, ""))

        # 4. Model & Memory Parameters
        with st.container(key="settings_model_card"):
            st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
    <h3 class="stitch-card-title" style="margin-bottom:0;">4. Model & Memory Parameters</h3>
    <span style="font-size:0.7rem;font-weight:700;background:rgba(8,127,91,0.12);color:#087F5B;padding:2px 8px;border-radius:4px;">Gemini 1.5</span>
</div>
<p class="stitch-card-sub" style="margin-bottom:16px;">Generative foundational LLM & conversational session controls.</p>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div style="background:{T['surface_alt']};border:1px solid {T['border']};border-radius:10px;padding:12px;margin-bottom:14px;font-size:0.8rem;line-height:1.6;color:{T['text_muted']};">
    <b>LLM Model:</b> {LLM_MODEL} (Google DeepMind)<br>
    <b>Sampling Temperature:</b> 0.15 (Deterministic & factual domain responses)<br>
    <b>Embedding Engine:</b> {EMBED_MODEL} ({EMBED_DIM}-dimensional)
</div>
""", unsafe_allow_html=True)

            n_turns = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
            st.write(f"💬 **Active Conversation:** {n_turns} turns in memory")
            if st.button("🗑️ Clear Conversation History", key="cfg_clear_chat_btn", use_container_width=True):
                st.session_state.messages = []
                st.session_state.chat_history = ChatMessageHistory()
                st.session_state.latest_sources = []
                fb_keys = [k for k in st.session_state if k.startswith("_fb_submitted_")]
                for k in fb_keys:
                    del st.session_state[k]
                st.session_state.pop("_last_rewritten_query", None)
                st.session_state.pop("pending_prompt", None)
                st.session_state.pop("_compare_toggle_widget", None)
                st.success("Conversation history cleared.")
                st.rerun()

            # User feedback summary
            feedback_list = st.session_state.get("user_feedback", [])
            if feedback_list:
                pos = sum(1 for f in feedback_list if f["score"] == 1)
                total = len(feedback_list)
                st.caption(f"⭐ **Feedback:** {total} ratings submitted ({pos/total*100:.0f}% positive)")
