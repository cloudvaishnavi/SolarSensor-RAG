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

# Phase 2+3+4 — new additive imports (never modifies existing backend)
from ui.components import _render_sources, _render_context_chips, _render_feedback_widget, _render_retrieval_mode_badge, _render_failure_loop_result
from ui.sidebar import render_sidebar


# --------------------------------------------------
# Helpers
# --------------------------------------------------

LOGO_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")
PIPELINE_GRAPHIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pipeline_graphic.jpg")
SOLAR_HEX_GRAPHIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "solar_hexagons.jpg")

from backend.vectorstore import create_vector_store, _parse_retry_delay, DOCS_FOLDER
from backend.chains import _call_direct_llm, build_qa_chain

os.makedirs(DOCS_FOLDER, exist_ok=True)

# --------------------------------------------------
# Page Config
# --------------------------------------------------
page_icon_img = Image.open(LOGO_PATH) if os.path.exists(LOGO_PATH) else "☀️"

st.set_page_config(
    page_title="SolarSense RAG",
    page_icon=page_icon_img,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# THEME SYSTEM
# --------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

from ui.theme import THEMES, get_css
T = THEMES[st.session_state.theme]

_css = get_css(st.session_state.theme)
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

# Load knowledge base
# --------------------------------------------------
if "kb_loaded" not in st.session_state:
    st.session_state.kb_loaded = False

if not st.session_state.kb_loaded:
    with st.spinner("Loading knowledge base…"):
        vectorstore, doc_count, doc_names = create_vector_store()
    st.session_state.kb_loaded = True
else:
    vectorstore, doc_count, doc_names = create_vector_store()

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
render_sidebar(vectorstore, doc_count, doc_names, T, LOGO_PATH)

# --------------------------------------------------
# Top Bar
# --------------------------------------------------
kb_live = vectorstore is not None

top_col_main, top_col_toggle = st.columns([9, 1])
with top_col_main:
    logo_b64 = img_to_b64(LOGO_PATH) if os.path.exists(LOGO_PATH) else ""
    logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:40px;height:40px;border-radius:4px;object-fit:cover;margin-right:14px;" />' if logo_b64 else ""
    st.markdown(f"""
<div class="top-bar">
    <div style="display:flex; align-items:center;">
        {logo_html}
        <div>
            <div class="top-bar-title">SolarSense RAG</div>
            <div class="top-bar-tagline">Intelligent Rooftop Solar Knowledge Assistant</div>
            <div class="badge-row" style="margin-top:8px;">
                <span class="badge badge-green">MNRE Grounded</span>
                <span class="badge badge-blue">Gemini Flash</span>
                <span class="badge">FAISS · MMR</span>
            </div>
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:12px;">
        <span class="kb-pill">
            <span class="kb-pill-dot" style="background:{'#10B981' if kb_live else T['text_dim']};"></span>
            Knowledge Base · {'Live' if kb_live else 'Offline'}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

with top_col_toggle:
    toggle_icon_main = "☀️" if st.session_state.theme == "dark" else "🌙"
    if st.button(toggle_icon_main, key="theme_toggle_main", help="Toggle light / dark theme"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

# --------------------------------------------------
# Metrics Row (4 cards)
# --------------------------------------------------
_display_chunk   = st.session_state.get("chunk_size", 900)
_display_overlap = st.session_state.get("chunk_overlap", 180)

retrieval_mode_display = st.session_state.get("retrieval_mode", "Dense only")

card_style = (
    f"background:{T['surface']};border:1px solid {T['border']};border-radius:4px;"
    f"padding:20px 24px;"
)
label_style = (
    f"font-size:0.7rem;color:{T['text_muted']};text-transform:uppercase;"
    f"letter-spacing:0.5px;font-weight:700;margin-bottom:8px;"
)
val_style = f"font-size:2rem;font-weight:700;color:{T['text']};line-height:1;"
sub_style = f"font-size:0.75rem;color:{T['text_dim']};margin-top:4px;"

mc1, mc2, mc3, mc4 = st.columns(4)
with mc1:
    st.markdown(
        f"<div style='{card_style}'>"
        f"<div style='{label_style}'>Documents Ingested</div>"
        f"<div style='{val_style}'>{doc_count}</div>"
        f"<div style='{sub_style}'>chunks indexed</div>"
        f"</div>", unsafe_allow_html=True
    )
with mc2:
    st.markdown(
        f"<div style='{card_style}'>"
        f"<div style='{label_style}'>Chunk Size</div>"
        f"<div style='{val_style}'>{_display_chunk}</div>"
        f"<div style='{sub_style}'>{_display_overlap} overlap</div>"
        f"</div>", unsafe_allow_html=True
    )
with mc3:
    st.markdown(
        f"<div style='{card_style}'>"
        f"<div style='{label_style}'>Retrieval Mode</div>"
        f"<div style='font-size:1.1rem;font-weight:700;color:{T['technical']};line-height:1.2;margin-bottom:4px;'>{retrieval_mode_display}</div>"
        f"<div style='{sub_style}'>k=5 · fetch_k=20</div>"
        f"</div>", unsafe_allow_html=True
    )
with mc4:
    kb_color = T['accent'] if kb_live else T['text_dim']
    kb_label = '● Live' if kb_live else '○ Offline'
    st.markdown(
        f"<div style='{card_style}'>"
        f"<div style='{label_style}'>Vector DB Status</div>"
        f"<div style='font-size:1.4rem;font-weight:700;color:{kb_color};line-height:1.2;'>{kb_label}</div>"
        f"<div style='{sub_style}'>FAISS index</div>"
        f"</div>", unsafe_allow_html=True
    )

st.markdown("<div style='margin-bottom:28px;'></div>", unsafe_allow_html=True)

# --------------------------------------------------
# QA Chain with Conversational Memory
# --------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

if "latest_sources" not in st.session_state:
    st.session_state.latest_sources = []

qa_chain, retriever_ref = build_qa_chain(vectorstore)

# --------------------------------------------------
# Chat Interface
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Compare mode
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False

# --------------------------------------------------
# Empty state / landing view
# --------------------------------------------------
if len(st.session_state.messages) == 0:
    # Knowledge Pipeline section
    st.markdown(
        f"<div style='font-size:0.75rem;font-weight:700;text-transform:uppercase;"
        f"letter-spacing:0.6px;color:{T['text_muted']};margin-bottom:14px;'>Knowledge Pipeline</div>",
        unsafe_allow_html=True,
    )

    # Graphic banner
    if os.path.exists(PIPELINE_GRAPHIC):
        pipeline_b64 = img_to_b64(PIPELINE_GRAPHIC)
        st.markdown(
            f"<div style='border-radius:4px;overflow:hidden;border:1px solid {T['border']};margin-bottom:20px;'>"
            f"<img src='data:image/jpeg;base64,{pipeline_b64}' style='width:100%;height:180px;object-fit:cover;display:block;' />"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Pipeline nodes
    st.markdown(f"""
<div class="pipeline-row">
    <div class="pipeline-node"><div class="pipeline-node-icon">📁</div><div class="pipeline-node-label">Documents</div></div>
    <div class="pipeline-connector">→</div>
    <div class="pipeline-node"><div class="pipeline-node-icon">🔍</div><div class="pipeline-node-label">Chunking & Embed</div></div>
    <div class="pipeline-connector">→</div>
    <div class="pipeline-node"><div class="pipeline-node-icon">🗄️</div><div class="pipeline-node-label">FAISS Index</div></div>
    <div class="pipeline-connector">→</div>
    <div class="pipeline-node"><div class="pipeline-node-icon">🤖</div><div class="pipeline-node-label">Gemini LLM</div></div>
    <div class="pipeline-connector">→</div>
    <div class="pipeline-node"><div class="pipeline-node-icon">✅</div><div class="pipeline-node-label">Grounded Answer</div></div>
</div>
""", unsafe_allow_html=True)

    # Solar hexagon graphic
    if os.path.exists(SOLAR_HEX_GRAPHIC):
        hex_b64 = img_to_b64(SOLAR_HEX_GRAPHIC)
        left_col, right_col = st.columns([2, 1])
        with left_col:
            st.markdown(
                f"<div style='font-size:0.75rem;font-weight:700;text-transform:uppercase;"
                f"letter-spacing:0.6px;color:{T['text_muted']};margin-bottom:14px;'>Suggested Inquiries</div>",
                unsafe_allow_html=True,
            )
            suggested = [
                ("PM Surya Ghar", "How much subsidy is available?", "What is the subsidy under PM Surya Ghar?"),
                ("Battery & Dispatch", "Explain Backup Priority mode", "What is Backup Priority mode?"),
                ("Monsoon", "How does monsoon pre-charge work?", "How does monsoon pre-charge work?"),
                ("Solar Economics", "What is Cost-Save mode?", "What is Cost-Save mode?"),
            ]
            sc1, sc2 = st.columns(2)
            for idx, (cat, label, query) in enumerate(suggested):
                with (sc1 if idx % 2 == 0 else sc2):
                    st.markdown(
                        f"<div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;"
                        f"letter-spacing:0.5px;color:{T['text_dim']};margin-bottom:4px;'>{cat}</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button(label, key=f"suggested_{cat}"):
                        st.session_state["pending_prompt"] = query
        with right_col:
            st.markdown(
                f"<div style='border-radius:4px;overflow:hidden;border:1px solid {T['border']};'>"
                f"<img src='data:image/jpeg;base64,{hex_b64}' style='width:100%;height:200px;object-fit:cover;display:block;' />"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"<div style='font-size:0.75rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.6px;color:{T['text_muted']};margin-bottom:14px;'>Suggested Inquiries</div>",
            unsafe_allow_html=True,
        )
        suggested = [
            ("PM Surya Ghar", "How much subsidy is available?", "What is the subsidy under PM Surya Ghar?"),
            ("Battery & Dispatch", "Explain Backup Priority mode", "What is Backup Priority mode?"),
            ("Monsoon", "How does monsoon pre-charge work?", "How does monsoon pre-charge work?"),
            ("Solar Economics", "What is Cost-Save mode?", "What is Cost-Save mode?"),
        ]
        sc1, sc2, sc3, sc4 = st.columns(4)
        for col, (cat, label, query) in zip([sc1, sc2, sc3, sc4], suggested):
            with col:
                st.caption(cat)
                if st.button(label, key=f"suggested_{cat}"):
                    st.session_state["pending_prompt"] = query

    st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------
# Compare mode toggle
# --------------------------------------------------
_cmp_on = st.session_state.compare_mode

_on_badge  = f"<span style='background:{T['accent_soft']};color:{T['accent']};font-weight:700;border-radius:2px;padding:2px 8px;font-size:0.75rem;border:1px solid {T['accent']};'>ON</span>"
_off_badge = f"<span style='background:{T['surface']};color:{T['text_dim']};font-weight:600;border-radius:2px;padding:2px 8px;font-size:0.75rem;border:1px solid {T['border']};'>OFF</span>"
_badge_html = _on_badge if _cmp_on else _off_badge
_desc = (
    "Side-by-side grounded vs. ungrounded answer shown below each response."
    if _cmp_on else
    "Only the grounded RAG answer is shown (recommended for production use)."
)

st.markdown(
    f"<div style='display:flex; align-items:center; justify-content:space-between; gap:12px; "
    f"background:{T['surface']}; border:1px solid {'#10B981' if _cmp_on else T['border']}; "
    f"border-radius:4px; padding:14px 20px; margin-bottom:12px;'>"
    f"<div style='display:flex; align-items:center; gap:14px;'>"
    f"<span style='font-size:1.2rem;'>🔍</span>"
    f"<div>"
    f"<div style='font-size:0.9rem; font-weight:700; color:{T['text']}; margin-bottom:3px;'>Compare: RAG vs Direct LLM &nbsp;{_badge_html}</div>"
    f"<div style='font-size:0.78rem; color:{T['text_muted']};'>{_desc}</div>"
    f"</div></div>"
    f"<div style='font-size:0.72rem; color:{T['text_dim']}; white-space:nowrap;'>Toggle →</div>"
    f"</div>",
    unsafe_allow_html=True,
)
_new_compare = st.toggle(
    "Compare: RAG vs Direct LLM",
    value=_cmp_on,
    key="_compare_toggle_widget",
    help="When ON, each answer includes a side-by-side comparison with an ungrounded direct LLM response.",
)
if _new_compare != _cmp_on:
    st.session_state.compare_mode = _new_compare
    st.rerun()
if _cmp_on:
    st.caption("⚠️ The Grounded (RAG) answer is the authoritative response. The Direct LLM answer has no access to your documents and may be incomplete or inaccurate.")

# --------------------------------------------------
# Render existing conversation
# --------------------------------------------------
user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
asst_idx  = 0
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            _render_context_chips(msg.get("sources", []), msg["content"])
            _sources = msg.get("sources", [])
            _annotated = _highlight_answer_phrases(msg["content"], _sources)
            st.markdown(_annotated, unsafe_allow_html=bool(_sources))
            _render_sources(_sources, msg["content"])

            if msg.get("direct_answer"):
                with st.expander("🔍 RAG vs Direct LLM Comparison", expanded=True):
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
                        <div class="compare-warning">ℹ️ The direct answer uses general model knowledge without access to your documents. It may be incomplete, outdated, or inaccurate. Always prefer the Grounded (RAG) answer.</div>
                        """, unsafe_allow_html=True)

            rewritten = msg.get("rewritten_query", "")
            if rewritten and rewritten != msg.get("original_question", rewritten):
                with st.expander("🔎 Rewritten query used for retrieval", expanded=False):
                    st.code(rewritten, language=None)

            q_for_fb = user_msgs[asst_idx]["content"] if asst_idx < len(user_msgs) else ""
            _render_feedback_widget(asst_idx, q_for_fb, msg["content"])
            asst_idx += 1
        else:
            st.markdown(msg["content"])

prompt = None
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")
user_input = st.chat_input("Ask about rooftop solar, PM Surya Ghar, dispatch modes, battery sizing…")
if user_input:
    prompt = user_input

if prompt:
    if qa_chain is None:
        st.warning("⚠️ Knowledge base is offline. Upload documents via the sidebar to get started.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            retrieval_mode    = st.session_state.get("retrieval_mode", "Dense only")
            rerank_top_k      = st.session_state.get("rerank_top_k", 5)
            hybrid_alpha      = st.session_state.get("hybrid_alpha", 0.7)
            failure_loop_on   = st.session_state.get("failure_loop_enabled", False)
            fail_faith_thr    = st.session_state.get("fail_faith_threshold", 1)
            fail_relev_thr    = st.session_state.get("fail_relev_threshold", 2)
            fail_loop_action  = st.session_state.get("fail_loop_action", "rephrase")

            with st.spinner("🔍 Retrieving relevant knowledge & generating grounded answer…"):
                st.session_state.latest_sources = []
                st.session_state["_last_rewritten_query"] = prompt
                success = False
                answer  = ""
                sources = []
                retrieved_context = ""

                # PATH A: Dense-only (original, untouched qa_chain path)
                if retrieval_mode == "Dense only":
                    for attempt in range(3):
                        try:
                            answer  = qa_chain.invoke(
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
                direct_answer   = ""

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
                                    "faith_threshold":  fail_faith_thr,
                                    "relev_threshold":  fail_relev_thr,
                                    "loop_action":      fail_loop_action,
                                    "retrieval_mode":   retrieval_mode,
                                    "reranker_enabled": retrieval_mode != "Dense only",
                                    "rerank_top_k":     rerank_top_k,
                                    "hybrid_alpha":     hybrid_alpha,
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
                    with st.expander("🔍 RAG vs Direct LLM Comparison", expanded=True):
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
                    with st.expander("🔎 Rewritten query used for retrieval", expanded=False):
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

# --------------------------------------------------
# Phase 1 — Evaluation Harness UI
# --------------------------------------------------
from ui.eval_page import render_eval_section
render_eval_section(T)