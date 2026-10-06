"""
eval/runner.py
--------------
Evaluation runner for SolarSensor-RAG — Phase 1 baseline.

Runs the eval set with checkpointing and resumability.

Usage (from project root, with venv active):
    python -m eval.runner
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is on the path when run as __main__
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from backend.vectorstore import create_vector_store, LLM_MODEL
from eval.metrics import (
    recall_at_k,
    judge_faithfulness,
    judge_relevance,
    judge_refusal,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

EVAL_SET_PATH      = os.path.join(_PROJECT_ROOT, "data", "eval_set.json")
MANUAL_GRADES_PATH = os.path.join(_PROJECT_ROOT, "eval", "manual_grades.json")

EVALUATION_ROOT    = os.path.join(_PROJECT_ROOT, "evaluation")
RESULTS_DIR        = os.path.join(EVALUATION_ROOT, "results")
SUMMARY_PATH       = os.path.join(EVALUATION_ROOT, "summary.json")

# Used by the UI if no separate summary is preferred, but UI will need updates.
RESULTS_PATH       = os.path.join(_PROJECT_ROOT, "eval", "results_baseline.json")


class QuotaExhaustedError(Exception):
    pass

# ---------------------------------------------------------------------------
# LLM judge setup (re-uses same model, temperature=0 for determinism)
# ---------------------------------------------------------------------------

def _make_llm_callable():
    """Returns a callable(prompt_str) -> str using Gemini with temperature=0."""
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.0, max_retries=0)
    prompt_tmpl = ChatPromptTemplate.from_messages([("human", "{text}")])
    chain = prompt_tmpl | llm | StrOutputParser()

    def _call(prompt_text: str) -> str:
        for attempt in range(5):
            try:
                return chain.invoke({"text": prompt_text})
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err or "500" in err or "503" in err:
                    wait = 30 + 15 * attempt
                    print(f"      Judge rate limit, retrying in {wait}s…", flush=True)
                    time.sleep(wait)
                    if attempt == 4:
                        raise QuotaExhaustedError(f"LLM Judge quota exhausted: {err}")
                    continue
                raise
        return ""

    return _call


# ---------------------------------------------------------------------------
# Context formatter (mirrors backend.chains._format_docs)
# ---------------------------------------------------------------------------

def _format_docs(docs) -> str:
    return "\n\n---\n\n".join(
        f"[Source {i+1}: {os.path.basename(d.metadata.get('source', 'unknown'))}]\n{d.page_content}"
        for i, d in enumerate(docs)
    )


# ---------------------------------------------------------------------------
# Eval-side retrieval helpers — Streamlit-free
# (backend/ files are NOT modified; we replicate only the non-st parts here)
# ---------------------------------------------------------------------------

# Module-level cache so the 85 MB model is downloaded and loaded only once
# per runner process, regardless of how many questions are evaluated.
_cross_encoder_cache: object = None
_cross_encoder_tried: bool = False


def _eval_load_cross_encoder():
    """Load CrossEncoder once per process. No @st.cache_resource, no Streamlit."""
    global _cross_encoder_cache, _cross_encoder_tried
    if _cross_encoder_tried:
        return _cross_encoder_cache
    _cross_encoder_tried = True
    try:
        from sentence_transformers.cross_encoder import CrossEncoder  # type: ignore
        print("      Loading cross-encoder model (first time — may download ~85 MB)…",
              flush=True)
        _cross_encoder_cache = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("      Cross-encoder loaded.", flush=True)
    except Exception as exc:
        print(f"      Cross-encoder unavailable ({exc}). Rerank will fall back to score order.",
              flush=True)
        _cross_encoder_cache = None
    return _cross_encoder_cache


def _eval_rerank(query: str, docs: list, top_k: int) -> list:
    """Re-score docs with cross-encoder and return top_k. Pure Python, no Streamlit."""
    if not docs:
        return docs
    model = _eval_load_cross_encoder()
    if model is None:
        return docs[:top_k]
    try:
        pairs = [(query, doc.page_content) for doc in docs]
        scores = model.predict(pairs)
        scored = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]
    except Exception:
        return docs[:top_k]


def _eval_build_bm25(vectorstore):
    """Build a BM25 index from the live vectorstore. No @st.cache_resource."""
    try:
        from rank_bm25 import BM25Okapi  # type: ignore
        from langchain_core.documents import Document
        import re

        store_dict = vectorstore.docstore._dict
        docs = [
            Document(page_content=doc.page_content,
                     metadata={"source": doc.metadata.get("source", "")})
            for doc in store_dict.values()
            if hasattr(doc, "page_content")
        ]
        if not docs:
            return None, []

        def _tok(text: str) -> list:
            return re.findall(r"[a-z0-9₹]+", text.lower())

        tokenised = [_tok(d.page_content) for d in docs]
        bm25 = BM25Okapi(tokenised)
        return bm25, docs
    except Exception as exc:
        print(f"      BM25 build failed ({exc}). Hybrid will fall back to dense.", flush=True)
        return None, []


def _eval_bm25_search(query: str, bm25, docs: list, top_k: int) -> list:
    """Return top_k BM25-ranked docs. No Streamlit."""
    import re
    if bm25 is None or not docs:
        return []
    tokens = re.findall(r"[a-z0-9₹]+", query.lower())
    if not tokens:
        return docs[:top_k]
    scores = bm25.get_scores(tokens)
    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:top_k]]


def _rrf_merge(ranked_lists: list, k: int = 60) -> list:
    """Reciprocal Rank Fusion — identical logic to backend/retrieval_pipeline.py."""
    scores: dict = {}
    doc_map: dict = {}
    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked, start=1):
            key = str(hash(doc.page_content))
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            doc_map[key] = doc
    merged = sorted(doc_map.items(), key=lambda x: scores[x[0]], reverse=True)
    return [doc for _, doc in merged]


# Module-level BM25 cache (built once per process for hybrid mode)
_bm25_cache: tuple = (None, [])
_bm25_built: bool = False


def _eval_retrieve(query: str, vectorstore, mode: str) -> list:
    """
    Dispatcher — selects retrieval path based on mode.

    dense_only    → FAISS MMR k=10, fetch_k=25  (IDENTICAL to original path)
    dense_rerank  → FAISS MMR fetch_k=20 candidates → cross-encoder → top 10
    hybrid_rerank → FAISS fetch_k=20 + BM25 top-20 → RRF merge → cross-encoder → top 10
    """
    global _bm25_cache, _bm25_built

    FETCH_K   = 20   # candidate pool for rerank modes
    FINAL_K   = 10   # final docs returned (keeps Recall@10 comparable)

    # ------------------------------------------------------------------
    # Path A: Dense-only — UNCHANGED from original working baseline
    # ------------------------------------------------------------------
    if mode == "dense_only":
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 10, "fetch_k": 25, "lambda_mult": 0.7},
        )
        return retriever.invoke(query)

    # ------------------------------------------------------------------
    # Path B: Dense + Rerank
    # ------------------------------------------------------------------
    if mode == "dense_rerank":
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": FETCH_K, "fetch_k": FETCH_K * 2, "lambda_mult": 0.7},
        )
        dense_docs = retriever.invoke(query)
        return _eval_rerank(query, dense_docs, top_k=FINAL_K)

    # ------------------------------------------------------------------
    # Path C: Hybrid + Rerank
    # ------------------------------------------------------------------
    if mode == "hybrid_rerank":
        # Dense candidates
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": FETCH_K, "fetch_k": FETCH_K * 2, "lambda_mult": 0.7},
        )
        dense_docs = retriever.invoke(query)

        # BM25 candidates (build index once per process)
        if not _bm25_built:
            print("      Building BM25 index…", flush=True)
            _bm25_cache = _eval_build_bm25(vectorstore)
            _bm25_built = True
        bm25_model, bm25_corpus = _bm25_cache
        bm25_docs = _eval_bm25_search(query, bm25_model, bm25_corpus, top_k=FETCH_K)

        # RRF merge
        if bm25_docs:
            candidate_docs = _rrf_merge([dense_docs, bm25_docs])
        else:
            candidate_docs = dense_docs

        return _eval_rerank(query, candidate_docs, top_k=FINAL_K)

    raise ValueError(f"Unknown retrieval mode: {mode}")




# ---------------------------------------------------------------------------
# Generation chain (no conversational memory — eval is single-turn)
# ---------------------------------------------------------------------------

_GEN_SYSTEM = """You are SolarSense, an expert AI assistant specialising in Indian rooftop solar systems and the PM Surya Ghar (MNRE) scheme.

**STRICT GROUNDING RULES (MUST FOLLOW):**
- You MUST answer the user's question ONLY using the context provided below.
- If the context does not contain the answer, you MUST reply EXACTLY with:
  "I don't have enough information in the loaded documents to answer that accurately. Please upload the relevant document or rephrase your question."
- Do NOT use outside knowledge. Do NOT speculate, guess, or invent answers.

Context from loaded documents:
{context}"""


def _make_gen_chain():
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0.15, max_retries=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", _GEN_SYSTEM),
        ("human", "{question}"),
    ])
    return prompt | llm | StrOutputParser()


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_evaluation(mode: str = "dense_only") -> dict:
    """
    Run the eval set incrementally, saving each question's result.
    Modes: dense_only, dense_rerank, hybrid_rerank
    """
    print("=" * 60)
    print(f"SolarSensor-RAG — Phase 1 Evaluation Runner (Mode: {mode})")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 60)

    if mode not in ["dense_only", "dense_rerank", "hybrid_rerank"]:
        raise ValueError(f"Invalid mode: {mode}")

    mode_dir = os.path.join(RESULTS_DIR, mode)
    os.makedirs(mode_dir, exist_ok=True)

    # --- Load eval set ---
    with open(EVAL_SET_PATH, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    questions = eval_data["questions"]
    print(f"\nLoaded {len(questions)} questions from {EVAL_SET_PATH}\n")

    # --- Load vector store (read-only, no rebuild triggered) ---
    print("Loading vector store (read-only)…")
    # create_vector_store is cached; calling it won't rebuild unless index missing
    vectorstore, doc_count, doc_names = create_vector_store()
    if vectorstore is None:
        raise RuntimeError("Vector store is None — make sure documents are indexed first.")
    print(f"Vector store loaded. {doc_count} document chunks indexed.\n")

    # --- Chains ---
    gen_chain = _make_gen_chain()
    llm_judge = _make_llm_callable()

    for i, q in enumerate(questions):
        qid       = q["id"]
        category  = q["category"]
        question  = q["question"]
        ideal_docs = q.get("ideal_source_docs", [])
        
        q_file_path = os.path.join(mode_dir, f"{qid}.json")
        if os.path.exists(q_file_path):
            with open(q_file_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                if saved_data.get("status") == "completed":
                    print(f"[{i+1:02d}/{len(questions)}] {qid} | Already completed. Skipping.")
                    continue

        print(f"[{i+1:02d}/{len(questions)}] {qid} | {category} | {question[:60]}…")

        try:
            # 1. Retrieval — dispatched by mode
            print("      Running retrieval...", flush=True)
            retrieved = _eval_retrieve(question, vectorstore, mode)
            context   = _format_docs(retrieved)

            # 2. Recall@5 and Recall@10
            r5  = recall_at_k(ideal_docs, retrieved, k=5)
            r10 = recall_at_k(ideal_docs, retrieved, k=10)

            # 3. Generation
            answer = ""
            for attempt in range(5):
                try:
                    answer = gen_chain.invoke({"question": question, "context": context})
                    break
                except Exception as e:
                    err = str(e)
                    if "429" in err or "RESOURCE_EXHAUSTED" in err or "500" in err or "503" in err:
                        wait = 30 + 15 * attempt
                        print(f"      Rate limit / server error, retrying in {wait}s…", flush=True)
                        time.sleep(wait)
                        if attempt == 4:
                            raise QuotaExhaustedError(f"Generation API limit exhausted: {err}")
                        continue
                    raise QuotaExhaustedError(f"Generation error: {err}")

            # 4. LLM-as-judge scoring
            faithfulness   = None
            relevance      = None
            refusal_correct = None

            if category in ("factual", "synthesis"):
                faithfulness = judge_faithfulness(question, context, answer, llm_judge)
                relevance    = judge_relevance(question, answer, llm_judge)
            elif category == "adversarial":
                refusal_correct = judge_refusal(question, answer, llm_judge)
                faithfulness = judge_faithfulness(question, context, answer, llm_judge)

            print(
                f"      R@5={r5} | R@10={r10} | Faith={faithfulness} | "
                f"Relev={relevance} | Refusal={refusal_correct}"
            )
            
            # Atomic save
            result_dict = {
                "question_id": qid,
                "category": category,
                "question": question,
                "retrieved_sources": [
                    os.path.basename(d.metadata.get("source", "unknown"))
                    for d in retrieved
                ],
                "generated_answer": answer,
                "faithfulness": faithfulness,
                "relevance": relevance,
                "refusal_correct": refusal_correct,
                "recall_at_5": r5,
                "recall_at_10": r10,
                "retrieval_mode": mode,
                "model_name": LLM_MODEL,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            tmp_path = q_file_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, q_file_path)

            # Polite delay to avoid rate limits between questions
            if i < len(questions) - 1:
                time.sleep(4)

        except QuotaExhaustedError as e:
            print(f"\nAPI Quota Exhausted or Persistent Error: {e}")
            print("Stopping cleanly. All progress up to now is saved.")
            break
        except Exception as e:
            print(f"\nUnexpected error processing {qid}: {e}")
            print("Stopping cleanly.")
            break

    # 5. Generate summary across all modes
    _generate_summary(eval_data)
    
    return {}

def _generate_summary(eval_data):
    """Reads all completed questions for all modes and generates summary.json"""
    summary_out = {}
    
    from eval.metrics import compute_summary
    
    for m in ["dense_only", "dense_rerank", "hybrid_rerank"]:
        mode_dir = os.path.join(RESULTS_DIR, m)
        if not os.path.exists(mode_dir):
            continue
            
        completed_results = []
        for filename in os.listdir(mode_dir):
            if filename.endswith(".json"):
                with open(os.path.join(mode_dir, filename), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue
                    if data.get("status") == "completed":
                        # Compute ideal_docs using eval_data if necessary, but metrics just uses recall values directly
                        # Wait, recall_at_k values are not inside `data`, we need to compute them? No, we didn't save recall_at_5 in data!
                        # Let's save recall_at_5 and recall_at_10 in result_dict in run_evaluation? 
                        # The user asked for "retrieved source/document/chunk IDs (if available)".
                        # Actually we can just re-compute recall if we map qid -> ideal_docs.
                        qid = data["question_id"]
                        ideal_docs = []
                        for q in eval_data["questions"]:
                            if q["id"] == qid:
                                ideal_docs = q.get("ideal_source_docs", [])
                                break
                        
                        # Just append to mock the compute_summary input
                        completed_results.append({
                            "id": qid,
                            "category": data["category"],
                            "faithfulness": data.get("faithfulness"),
                            "relevance": data.get("relevance"),
                            "refusal_correct": data.get("refusal_correct"),
                            # Re-compute recall from retrieved sources vs ideal docs is harder because retrieved_sources are just strings here.
                            # But wait, recall_at_5 in metrics.py takes Document objects. 
                            # It's better if we just save recall_at_5 in the json!
                            "recall_at_5": data.get("recall_at_5"),
                            "recall_at_10": data.get("recall_at_10")
                        })
                        
        if completed_results:
            total_questions_in_set = len(eval_data["questions"])
            completed_count = len(completed_results)
            unfinished_count = total_questions_in_set - completed_count
            
            s = compute_summary(completed_results)
            summary_out[m] = {
                "completed_questions": completed_count,
                "unfinished_questions": unfinished_count,
                "Recall@5": s.get("recall_at_5"),
                "Recall@10": s.get("recall_at_10"),
                "Faithfulness": s.get("faithfulness_mean"),
                "Relevance": s.get("relevance_mean"),
                "Refusal Accuracy": s.get("refusal_accuracy"),
            }
            
    os.makedirs(EVALUATION_ROOT, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_out, f, indent=2, ensure_ascii=False)
    print(f"\nSummary written to: {SUMMARY_PATH}")
    print(json.dumps(summary_out, indent=2))


# ---------------------------------------------------------------------------
# Manual grades loader (for UI display)
# ---------------------------------------------------------------------------

def load_manual_grades() -> dict | None:
    if os.path.exists(MANUAL_GRADES_PATH):
        with open(MANUAL_GRADES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def load_baseline_results() -> dict | None:
    """
    Load results for the Evaluation UI from summary.json and per-question files.

    Fixes applied:
      - Recall@5 / Recall@10 are multiplied by 100 (stored as 0–1 fractions).
      - All three modes (dense_only, dense_rerank, hybrid_rerank) are returned
        so the Before vs After table can show real numbers.
      - per_question is populated by reading every completed JSON from
        evaluation/results/dense_only/ so score-distribution charts work.
    """
    if not os.path.exists(SUMMARY_PATH):
        return None

    with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
        s = json.load(f)

    def _mode_to_pcts(mode_data: dict) -> dict:
        """Convert a mode block from summary.json into display-ready percentages."""
        r5  = mode_data.get("Recall@5")
        r10 = mode_data.get("Recall@10")
        fth = mode_data.get("Faithfulness")
        rel = mode_data.get("Relevance")
        ref = mode_data.get("Refusal Accuracy")
        return {
            # BUG FIX 1: Recall values are 0–1 fractions → multiply by 100
            "recall_at_5":          r5  * 100 if r5  is not None else None,
            "recall_at_10":         r10 * 100 if r10 is not None else None,
            "faithfulness_pct":     fth * 100 if fth is not None else None,
            "relevance_pct":        rel / 3.0 * 100 if rel is not None else None,
            "refusal_accuracy_pct": ref * 100 if ref is not None else None,
        }

    dense       = s.get("dense_only",   {})
    dense_rerank = s.get("dense_rerank", {})
    hybrid_rerank = s.get("hybrid_rerank", {})

    # BUG FIX 3: Load per-question data from the individual result files
    per_question = []
    dense_results_dir = os.path.join(RESULTS_DIR, "dense_only")
    if os.path.isdir(dense_results_dir):
        for fname in sorted(os.listdir(dense_results_dir)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(dense_results_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            if data.get("status") != "completed":
                continue
            r5_val  = data.get("recall_at_5")
            r10_val = data.get("recall_at_10")
            per_question.append({
                "id":               data.get("question_id", fname.replace(".json", "")),
                "category":         data.get("category", "factual"),
                "question":         data.get("question", ""),
                "answer":           data.get("generated_answer", ""),
                "faithfulness":     data.get("faithfulness"),
                "relevance":        data.get("relevance"),
                "refusal_correct":  data.get("refusal_correct"),
                # Recall stored as 0–1 fraction in files; keep raw here,
                # the UI formats them with :.0f after × 100 for display
                "recall_at_5":      r5_val  * 100 if r5_val  is not None else None,
                "recall_at_10":     r10_val * 100 if r10_val is not None else None,
                "retrieved_sources": data.get("retrieved_sources", []),
                "ideal_source_docs": data.get("ideal_source_docs", []),
            })

    return {
        # BUG FIX 1: dense_only summary with Recall as percentages
        "summary": _mode_to_pcts(dense),
        # BUG FIX 2: all three mode summaries for Before vs After table
        "summary_all_modes": {
            "dense_only":    _mode_to_pcts(dense),
            "dense_rerank":  _mode_to_pcts(dense_rerank),
            "hybrid_rerank": _mode_to_pcts(hybrid_rerank),
        },
        # BUG FIX 3: per-question list populated from files
        "per_question": per_question,
        "_meta": {
            "model":     LLM_MODEL,
            "retrieval": "checkpointed",
            "run_at":    dense.get("run_at", ""),
        },
    }

if __name__ == "__main__":
    run_evaluation(mode="hybrid_rerank")

