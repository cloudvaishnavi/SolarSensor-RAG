import streamlit as st
import os
import shutil
from langchain_community.chat_message_histories import ChatMessageHistory
from backend.vectorstore import INDEX_PATH, DOCS_FOLDER, LLM_MODEL, EMBED_MODEL, EMBED_DIM
from backend.text_utils import img_to_b64


def render_sidebar(vectorstore, doc_count: int, doc_names: list, T: dict, LOGO_PATH: str):
    with st.sidebar:
        # ----------------------------------------------------------------
        # HEADER — Logo + App name
        # ----------------------------------------------------------------
        logo_b64 = img_to_b64(LOGO_PATH) if os.path.exists(LOGO_PATH) else ""
        if logo_b64:
            st.markdown(
                f"""
<div class="sidebar-logo-wrap">
    <img src="data:image/jpeg;base64,{logo_b64}" class="sidebar-logo-img" />
    <div>
        <div class="sidebar-logo-name">SolarSense RAG</div>
        <div class="sidebar-logo-sub">Intelligent Rooftop Solar Knowledge Assistant</div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
<div class="sidebar-logo-wrap">
    <span style="font-size:2rem;">☀️</span>
    <div>
        <div class="sidebar-logo-name">SolarSense RAG</div>
        <div class="sidebar-logo-sub">Intelligent Rooftop Solar Knowledge Assistant</div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<div style='width:100%;height:1px;background:{T['border']};margin-bottom:8px;'></div>",
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------------------
        # KNOWLEDGE BASE STATUS
        # ----------------------------------------------------------------
        st.markdown(
            '<div class="sidebar-nav-label"><span class="nav-icon">▣</span>Knowledge Base</div>',
            unsafe_allow_html=True,
        )
        if vectorstore is not None:
            st.markdown(
                f'<div class="info-row"><span class="info-dot info-dot-on"></span>Active · {doc_count} document(s)</div>',
                unsafe_allow_html=True,
            )
            if doc_names:
                with st.expander("View ingested files", expanded=False):
                    st.markdown(
                        '<div class="kb-doc-list">'
                        + "".join(f"📄 {n}<br>" for n in doc_names)
                        + "</div>",
                        unsafe_allow_html=True,
                    )
        elif doc_count > 0:
            st.markdown(
                '<div class="info-row"><span class="info-dot info-dot-off"></span>Offline — indexing failed, please retry</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="info-row"><span class="info-dot info-dot-off"></span>Offline — no documents yet</div>',
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------------------
        # UPLOAD SECTION
        # ----------------------------------------------------------------
        st.markdown(
            '<div class="sidebar-nav-label"><span class="nav-icon">↥</span>File Uploads</div>',
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Upload solar knowledge documents",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded:
            for f in uploaded:
                with open(os.path.join(DOCS_FOLDER, f.name), "wb") as out:
                    out.write(f.getbuffer())
            if os.path.exists(INDEX_PATH):
                backup_path = INDEX_PATH + "_backup"
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path, ignore_errors=True)
                shutil.move(INDEX_PATH, backup_path)
            st.cache_resource.clear()
            st.success(f"✅ {len(uploaded)} file(s) uploaded. Rebuilding index…")
            st.rerun()

        # ----------------------------------------------------------------
        # ADVANCED CHUNKING SETTINGS
        # ----------------------------------------------------------------
        with st.expander("⚙️ Advanced Chunking Settings", expanded=False):
            chunk_strategy = st.selectbox(
                "Strategy",
                ["Standard (Default)", "Large Chunks (PDF-heavy)"],
                index=0,
            )
            if chunk_strategy == "Standard (Default)":
                def_chunk = 900
                def_ovlap = 180
                msg = "**900 / 180** is the recommended baseline for this domain."
            else:
                def_chunk = 1500
                def_ovlap = 300
                msg = "**1500 / 300** keeps more surrounding context per chunk."

            c_size = st.number_input("Chunk Size (chars)", value=def_chunk, min_value=100, step=50)
            c_overlap = st.number_input("Chunk Overlap (chars)", value=def_ovlap, min_value=0, step=20)
            st.caption(msg)

            if st.button("🔄 Rebuild Index with These Settings"):
                st.session_state.chunk_size = c_size
                st.session_state.chunk_overlap = c_overlap
                if os.path.exists(INDEX_PATH):
                    shutil.rmtree(INDEX_PATH, ignore_errors=True)
                st.cache_resource.clear()
                st.session_state.kb_loaded = False
                st.rerun()

        # ----------------------------------------------------------------
        # RETRIEVAL SETTINGS
        # ----------------------------------------------------------------
        with st.expander("⚡ Retrieval Settings", expanded=False):
            st.markdown(
                f"<div style='font-size:0.78rem; color:{T['text_muted']}; margin-bottom:8px;'>"
                "Control how documents are retrieved and ranked before generation.</div>",
                unsafe_allow_html=True,
            )

            retrieval_mode = st.selectbox(
                "Retrieval Mode",
                options=["Dense only", "Dense + Rerank", "Hybrid + Rerank"],
                index=0,
                key="retrieval_mode",
                help=(
                    "Dense only: standard FAISS MMR (original path). "
                    "Dense + Rerank: FAISS retrieves 20, cross-encoder reorders → top-k. "
                    "Hybrid + Rerank: FAISS + BM25 merged with RRF → cross-encoder → top-k."
                ),
            )

            if retrieval_mode in ("Dense + Rerank", "Hybrid + Rerank"):
                st.slider(
                    "Top-K after Rerank",
                    min_value=1,
                    max_value=15,
                    value=st.session_state.get("rerank_top_k", 5),
                    step=1,
                    key="rerank_top_k",
                    help="Number of documents passed to the LLM after reranking.",
                )
            else:
                if "rerank_top_k" not in st.session_state:
                    st.session_state.rerank_top_k = 5

            if retrieval_mode == "Hybrid + Rerank":
                st.slider(
                    "Dense Weight (α)",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.get("hybrid_alpha", 0.7),
                    step=0.05,
                    key="hybrid_alpha",
                    help="α=1.0 → dense only; α=0.0 → BM25 only; α=0.7 recommended.",
                )
            else:
                if "hybrid_alpha" not in st.session_state:
                    st.session_state.hybrid_alpha = 0.7

            mode_info = {
                "Dense only": "🔵 **FAISS MMR** — original retrieval path, unchanged.",
                "Dense + Rerank": "🟡 **FAISS → Cross-Encoder** — fetches top-20 dense candidates, then scores each with `cross-encoder/ms-marco-MiniLM-L-6-v2`.",
                "Hybrid + Rerank": "🟢 **FAISS + BM25 → RRF → Cross-Encoder** — dense and keyword results merged via Reciprocal Rank Fusion, then reranked.",
            }
            st.caption(mode_info.get(retrieval_mode, ""))

        # ----------------------------------------------------------------
        # FAILURE-AWARE LOOP
        # ----------------------------------------------------------------
        with st.expander("🔁 Failure-Aware Loop", expanded=False):
            st.markdown(
                f"<div style='font-size:0.78rem; color:{T['text_muted']}; margin-bottom:8px;'>"
                "Score answers post-generation and auto-correct when quality is low.</div>",
                unsafe_allow_html=True,
            )

            failure_loop_enabled = st.toggle(
                "Enable Failure-Aware Loop",
                value=st.session_state.get("failure_loop_enabled", False),
                key="failure_loop_enabled",
                help="When on, each answer is scored and a rephrase+retry or refusal is triggered if below threshold.",
            )

            if failure_loop_enabled:
                st.markdown(
                    f"<div style='font-size:0.74rem; font-weight:700; color:{T['text_dim']}; margin:6px 0 2px;'>Quality Thresholds</div>",
                    unsafe_allow_html=True,
                )
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input(
                        "Faithfulness ≥",
                        min_value=0,
                        max_value=1,
                        value=st.session_state.get("fail_faith_threshold", 1),
                        step=1,
                        key="fail_faith_threshold",
                        help="0=any answer passes, 1=must be grounded (recommended).",
                    )
                with col2:
                    st.number_input(
                        "Relevance ≥",
                        min_value=0,
                        max_value=3,
                        value=st.session_state.get("fail_relev_threshold", 2),
                        step=1,
                        key="fail_relev_threshold",
                        help="0–3 scale. 2=partially addresses question (recommended baseline).",
                    )

                st.radio(
                    "When score is low:",
                    options=["rephrase", "refuse"],
                    format_func=lambda x: {
                        "rephrase": "🔄 Rephrase query & retry once",
                        "refuse":   "🚫 Emit clear refusal message",
                    }[x],
                    index=0,
                    key="fail_loop_action",
                    horizontal=True,
                    help="'Rephrase & retry' makes one additional LLM call.",
                )
                st.caption(
                    "⚠️ Enabling this loop adds 2 LLM judge calls per answer."
                )

        # ----------------------------------------------------------------
        # USER FEEDBACK
        # ----------------------------------------------------------------
        with st.expander("💬 User Feedback", expanded=False):
            feedback_list = st.session_state.get("user_feedback", [])
            if not feedback_list:
                st.caption("No feedback submitted yet.")
            else:
                pos = sum(1 for f in feedback_list if f["score"] == 1)
                neg = sum(1 for f in feedback_list if f["score"] == 0)
                total = len(feedback_list)
                avg = pos / total * 100
                st.markdown(
                    f"<div style='font-size:0.82rem; margin-bottom:4px;'>"
                    f"<b>{total}</b> response{'s' if total != 1 else ''} rated &nbsp;·&nbsp; "
                    f"<b style='color:{T['success']};'>{avg:.0f}%</b> positive"
                    f"</div>"
                    f"<div style='font-size:0.76rem; color:{T['text_muted']}; margin-bottom:8px;'>"
                    f"👍 {pos} helpful &nbsp;/&nbsp; 👎 {neg} not helpful"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("---")
                st.markdown(
                    f"<div style='font-size:0.68rem; font-weight:700; text-transform:uppercase; "
                    f"letter-spacing:0.5px; color:{T['text_dim']}; margin-bottom:6px;'>Recent Feedback</div>",
                    unsafe_allow_html=True,
                )
                for fb in reversed(feedback_list[-3:]):
                    emoji = "👍" if fb["score"] == 1 else "👎"
                    cmt   = fb.get("comment", "")
                    q_short = fb["question"][:50] + ("…" if len(fb["question"]) > 50 else "")
                    score_label = "Helpful" if fb["score"] == 1 else "Not helpful"
                    score_color = T["success"] if fb["score"] == 1 else T["error"]
                    ts = fb.get("timestamp", "")
                    ts_html = (
                        f'<span style="font-size:0.64rem; color:{T["text_dim"]}; float:right;">{ts[11:16] if len(ts) >= 16 else ts}</span>'
                        if ts else ""
                    )
                    cmt_html = (
                        f'<br><i style="font-size:0.74rem; color:{T["text_dim"]};">{cmt}</i>'
                        if cmt else ""
                    )
                    st.markdown(
                        f"<div style='font-size:0.78rem; margin-bottom:6px; padding:10px 12px; "
                        f"background:{T['surface_alt']}; border-radius:4px; border:1px solid {T['border']};'>"
                        f"{ts_html}"
                        f"<span style='color:{score_color}; font-weight:700;'>{emoji} {score_label}</span><br>"
                        f"<span style='color:{T['text_muted']};'>{q_short}</span>"
                        f"{cmt_html}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        # ----------------------------------------------------------------
        # CONVERSATION
        # ----------------------------------------------------------------
        with st.expander("💬 Conversation", expanded=False):
            n_turns = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
            st.markdown(
                f"<div style='font-size:0.8rem; color:{T['text_muted']}; margin-bottom:8px;'>"
                f"🗨️ <b>{n_turns}</b> turn{'s' if n_turns != 1 else ''} in history</div>",
                unsafe_allow_html=True,
            )
            if st.button("🗑️ Clear Conversation"):
                st.session_state.messages = []
                st.session_state.chat_history = ChatMessageHistory()
                st.session_state.latest_sources = []
                fb_keys = [k for k in st.session_state if k.startswith("_fb_submitted_")]
                for k in fb_keys:
                    del st.session_state[k]
                st.session_state.pop("_last_rewritten_query", None)
                st.session_state.pop("pending_prompt", None)
                st.session_state.pop("_compare_toggle_widget", None)
                st.rerun()

        # ----------------------------------------------------------------
        # INGESTION PIPELINE
        # ----------------------------------------------------------------
        with st.expander("⇢  Ingestion Pipeline", expanded=False):
            st.markdown("""
<div class="pipeline-chip-row">
    <span class="pipeline-chip">Loading</span><span class="pipeline-arrow">→</span>
    <span class="pipeline-chip">Extracting</span><span class="pipeline-arrow">→</span>
    <span class="pipeline-chip">Chunking</span><span class="pipeline-arrow">→</span>
    <span class="pipeline-chip">Embedding</span><span class="pipeline-arrow">→</span>
    <span class="pipeline-chip">Indexing</span><span class="pipeline-arrow">→</span>
    <span class="pipeline-chip">Ready</span>
</div>
<div style="font-size:0.74rem; color:#94A3B8; margin-top:8px;">Runs live above the chat during upload.</div>
""", unsafe_allow_html=True)

        # ----------------------------------------------------------------
        # PM SURYA GHAR CALCULATOR
        # ----------------------------------------------------------------
        with st.expander("⌘  PM Surya Ghar Calculator", expanded=False):
            system_kw = st.number_input("System Size (kWp)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
            if system_kw <= 2.0:
                subsidy = 30_000 * system_kw
                is_capped = False
            elif system_kw <= 3.0:
                subsidy = 60_000 + (system_kw - 2.0) * 18_000
                is_capped = (system_kw == 3.0)
            else:
                subsidy = 78_000
                is_capped = True
            est_cost   = system_kw * 55_000
            net_cost   = max(0.0, est_cost - subsidy)
            annual_save = system_kw * 1_400 * 7.5
            payback    = net_cost / annual_save if annual_save > 0 else 0
            cap_html   = '<span class="cap-badge">MAX CAP</span>' if is_capped else ""
            st.markdown(f"""
<div class="calc-card">
    <div class="calc-label">Central Subsidy (CFA)</div>
    <div class="calc-val">&#8377;{subsidy:,.0f} {cap_html}</div>
    <div class="calc-detail">
        &bull; System Cost: <b>&#8377;{est_cost:,.0f}</b><br>
        &bull; Net Out-of-Pocket: <b>&#8377;{net_cost:,.0f}</b><br>
        &bull; Annual Savings: <b>&#8377;{annual_save:,.0f}/yr</b><br>
        &bull; Payback Period: <span class="calc-payback">~{payback:.1f} yrs</span>
    </div>
</div>
""", unsafe_allow_html=True)
            st.caption("MNRE slabs · ₹30k/kW (≤2 kW) · ₹18k/kW (2–3 kW) · Max ₹78k cap")

        # ----------------------------------------------------------------
        # EXAMPLE QUESTIONS
        # ----------------------------------------------------------------
        with st.expander("☼  Example Questions", expanded=False):
            example_categories = [
                ("PM Surya Ghar", [
                    ("How much subsidy is available?", "What is the subsidy under PM Surya Ghar?"),
                ]),
                ("Battery & Dispatch", [
                    ("Explain Backup Priority mode", "What is Backup Priority mode?"),
                    ("Explain the dispatch modes", "Explain the different dispatch modes"),
                ]),
                ("Monsoon", [
                    ("How does monsoon pre-charge work?", "How does monsoon pre-charge work?"),
                ]),
                ("Solar Economics", [
                    ("What is Cost-Save mode?", "What is Cost-Save mode?"),
                    ("What is dust-loss penalty?", "What is dust-loss penalty?"),
                ]),
            ]
            for cat_label, questions in example_categories:
                st.markdown(f'<div class="sidebar-subcategory">{cat_label}</div>', unsafe_allow_html=True)
                for label, query in questions:
                    if st.button(label, key=f"ex_{cat_label}_{label}"):
                        st.session_state["pending_prompt"] = query

        # ----------------------------------------------------------------
        # SYSTEM STATUS
        # ----------------------------------------------------------------
        with st.expander("◉  System Status", expanded=False):
            kb_live = vectorstore is not None
            st.markdown(f"""
<div class="status-chip-row">
    <span class="status-chip">{'●' if kb_live else '○'} {'Live' if kb_live else 'Offline'}</span>
    <span class="status-chip">{LLM_MODEL}</span>
    <span class="status-chip">{EMBED_MODEL.split('/')[-1]} · {EMBED_DIM}d</span>
    <span class="status-chip">FAISS · MMR</span>
    <span class="status-chip">MNRE Grounded</span>
</div>
""", unsafe_allow_html=True)

        # ----------------------------------------------------------------
        # ARCHITECTURE & HOW IT WORKS
        # ----------------------------------------------------------------
        with st.expander("◈  Architecture & How It Works", expanded=False):
            st.markdown(f"""
<div class="arch-step">
  <div class="arch-num">1</div>
  <div class="arch-content">
    <b>Document Ingestion &amp; Text Extraction</b><br>PDF &amp; TXT files loaded via LangChain DirectoryLoader. Supports batch upload.
  </div>
</div>
<div class="arch-step">
  <div class="arch-num">2</div>
  <div class="arch-content">
    <b>Chunking</b><br>RecursiveCharacterTextSplitter · <b>900 characters / 180 overlap</b> (configurable via Advanced Settings).
    <div class="arch-why">
      900 keeps each chunk topically focused without cutting a sentence mid-thought. The 180-character overlap (20%) prevents a fact from being silently split across a chunk boundary.
    </div>
  </div>
</div>
<div class="arch-step">
  <div class="arch-num">3</div>
  <div class="arch-content">
    <b>Embeddings</b><br>Google <b>{EMBED_MODEL}</b> ({EMBED_DIM}-dim).
    <div class="arch-why">
      Document chunks and the user's query are embedded with the same model into the same vector space. Dimensionality is pinned explicitly so the FAISS index is never built with an ambiguous vector size.
    </div>
  </div>
</div>
<div class="arch-step">
  <div class="arch-num">4</div>
  <div class="arch-content">
    <b>FAISS Vector Store</b><br>Index persisted to disk (<code>faiss_index/</code>).
    <div class="arch-why">
      A signature file records which embedding model built the index — if the model is ever changed, the app detects the mismatch and rebuilds automatically.
    </div>
  </div>
</div>
<div class="arch-step">
  <div class="arch-num">5</div>
  <div class="arch-content">
    <b>MMR Retrieval</b><br>Maximal Marginal Relevance (k=5, fetch_k=20, λ=0.7).
    <div class="arch-why">
      MMR fetches a wider candidate pool (fetch_k=20) then greedily selects k=5 chunks that are relevant but diverse, so multi-part questions get coverage across different passages.
    </div>
  </div>
</div>
<div class="arch-step">
  <div class="arch-num">6</div>
  <div class="arch-content">
    <b>Query Rephrasing (Conversational Memory)</b><br>RunnableWithMessageHistory + a dedicated rephrase chain.
    <div class="arch-why">
      Before retrieval, a lightweight LLM call rewrites the latest question into a standalone one using chat history — so retrieval always searches with a self-contained query.
    </div>
  </div>
</div>
<div class="arch-step">
  <div class="arch-num">7</div>
  <div class="arch-content">
    <b>Gemini Generation</b><br><b>{LLM_MODEL}</b> · temperature 0.15.
    <div class="arch-why">
      Low temperature keeps answers deterministic and factual — consistency across repeated questions matters more than stylistic variety for a grounded assistant.
    </div>
  </div>
</div>
<div class="arch-step">
  <div class="arch-num">8</div>
  <div class="arch-content">
    <b>Grounded Answer</b>
    <div class="arch-why">
      The system prompt forbids answering from the model's own world knowledge and requires an exact fallback sentence when retrieved context doesn't cover the question.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ----------------------------------------------------------------
        # EVALUATION RESULTS
        # ----------------------------------------------------------------
        with st.expander("▥  Evaluation Results", expanded=False):
            eval_results = [
                ("What is Cost-Save mode?", "In-scope", "correct",
                 "Answer matched 01_dispatch_modes.txt exactly, correctly cited source."),
                ("How does monsoon pre-charge work?", "In-scope", "correct",
                 "Correctly explained pre-emptive charging logic with source citation."),
                ("What is the subsidy under PM Surya Ghar?", "In-scope", "correct",
                 "Correct slab figures (₹30k/kW, ₹18k/kW, ₹78k cap) matched source document."),
                ("Explain the different dispatch modes", "In-scope", "correct",
                 "Listed all modes with brief accurate descriptions from multiple retrieved chunks (MMR diversity)."),
                ("Compare Cost-Save and Backup Priority mode", "Multi-doc / follow-up", "partial",
                 "Correct on individual mode behavior; comparison structure could be tighter."),
                ("Explain the second one in more detail", "Follow-up (pronoun resolution)", "correct",
                 "Rephrase chain correctly resolved 'the second one' using prior turn before retrieval."),
                ("What is dust-loss penalty?", "In-scope", "correct",
                 "Correct definition and cited source document."),
                ("Explain Backup Priority mode", "In-scope", "correct",
                 "Accurate summary matching the source document's described behavior."),
                ("What documents power this system?", "In-scope (meta)", "correct",
                 "Correctly listed the ingested document names from the knowledge base."),
                ("How is the battery sized for a 3kW system?", "In-scope", "correct",
                 "Correctly retrieved and summarized sizing guidance from the loaded documents."),
                ("What is the payback period for a 5kW system?", "In-scope (calculator overlap)", "correct",
                 "Correctly grounded in document text rather than just echoing the sidebar calculator."),
                ("What's the weather in Bengaluru tomorrow?", "Out-of-scope", "declined",
                 "Correctly replied with refusal — no hallucination."),
            ]
            n_total    = len(eval_results)
            n_correct  = sum(1 for r in eval_results if r[2] == "correct")
            n_partial  = sum(1 for r in eval_results if r[2] == "partial")
            n_declined = sum(1 for r in eval_results if r[2] == "declined")

            st.markdown(f"""
<div class="eval-summary-row">
    <div class="eval-stat"><div class="eval-stat-val">{n_total}</div><div class="eval-stat-lbl">Total Test Questions</div></div>
    <div class="eval-stat"><div class="eval-stat-val" style="color:#10B981;">{n_correct}</div><div class="eval-stat-lbl">Fully Correct</div></div>
    <div class="eval-stat"><div class="eval-stat-val" style="color:#3B82F6;">{n_partial}</div><div class="eval-stat-lbl">Partially Correct</div></div>
    <div class="eval-stat"><div class="eval-stat-val" style="color:#94A3B8;">{n_declined}</div><div class="eval-stat-lbl">Correctly Refused</div></div>
</div>
""", unsafe_allow_html=True)
            st.caption("Manually evaluated against the loaded SolarSense knowledge base.")

            tag_map = {
                "correct":  ("✅ Correct",  "eval-tag-correct"),
                "partial":  ("⚠️ Partial",  "eval-tag-partial"),
                "declined": ("🚫 Correctly Refused", "eval-tag-declined"),
            }
            for q, category, verdict, note in eval_results:
                label, css_class = tag_map[verdict]
                st.markdown(f"""
<div class="eval-row">
    <span class="eval-tag {css_class}">{label}</span>
    <div>
        <div class="eval-q">{q} <span style="font-weight:400;font-size:0.72rem;"> · {category}</span></div>
        <div class="eval-note">{note}</div>
    </div>
</div>
""", unsafe_allow_html=True)
