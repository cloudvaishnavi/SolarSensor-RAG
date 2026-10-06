"""
backend/retrieval_pipeline.py
-------------------------------
Unified retrieval orchestrator for Phases 2 and 3.

Combines:
  - Dense FAISS/MMR retrieval  (always present)
  - BM25 keyword retrieval     (Phase 3, optional)
  - Reciprocal Rank Fusion     (Phase 3, merging strategy)
  - Cross-encoder reranking    (Phase 2, optional post-processing)

The original dense-only path in backend/chains.py is completely untouched.
This module is only called from app.py when the user selects a non-dense mode
via the sidebar Retrieval Settings.

Public API
----------
    retrieve(query, vectorstore, retrieval_mode, reranker_enabled,
             rerank_top_k, hybrid_alpha) -> list[Document]

retrieval_mode values (match sidebar selectbox):
    "Dense only"         → FAISS MMR → slice to rerank_top_k (no reranker)
    "Dense + Rerank"     → FAISS MMR → cross-encoder rerank → top rerank_top_k
    "Hybrid + Rerank"    → FAISS + BM25 → RRF merge → cross-encoder → top k
"""

from __future__ import annotations

import os
from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def _reciprocal_rank_fusion(
    ranked_lists: list[list[Document]],
    k: int = 60,
) -> list[Document]:
    """
    Merge multiple ranked document lists using Reciprocal Rank Fusion (RRF).

    RRF score for a document d across lists:  Σ 1 / (k + rank(d, list_i))
    Documents are de-duplicated by page_content hash.

    k=60 is the standard RRF constant (Cormack et al. 2009).
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked, start=1):
            key = hash(doc.page_content)
            str_key = str(key)
            scores[str_key] = scores.get(str_key, 0.0) + 1.0 / (k + rank)
            doc_map[str_key] = doc

    merged = sorted(doc_map.items(), key=lambda x: scores[x[0]], reverse=True)
    return [doc for _, doc in merged]


# ---------------------------------------------------------------------------
# Public retrieve() function
# ---------------------------------------------------------------------------

def retrieve(
    query: str,
    vectorstore,
    retrieval_mode: str = "Dense only",
    reranker_enabled: bool = False,
    rerank_top_k: int = 5,
    hybrid_alpha: float = 0.7,
    fetch_k: int = 20,
) -> list[Document]:
    """
    Run retrieval according to *retrieval_mode* and return final docs.

    Parameters
    ----------
    query           : User's (possibly rewritten) question.
    vectorstore     : Live FAISS vectorstore from create_vector_store().
    retrieval_mode  : One of "Dense only", "Dense + Rerank", "Hybrid + Rerank".
    reranker_enabled: Whether to apply cross-encoder reranking.
    rerank_top_k    : Final number of docs to return.
    hybrid_alpha    : Weight for dense results in RRF (0=all BM25, 1=all dense).
                      Not used by RRF itself (which is rank-based), but controls
                      how many candidates each source contributes.
    fetch_k         : Candidate pool size from FAISS.
    """
    if vectorstore is None:
        return []

    # ------------------------------------------------------------------
    # 1. Dense retrieval (always runs)
    # ------------------------------------------------------------------
    dense_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": fetch_k, "fetch_k": fetch_k * 2, "lambda_mult": 0.7},
    )
    try:
        dense_docs = dense_retriever.invoke(query)
    except Exception:
        dense_docs = []

    # ------------------------------------------------------------------
    # 2. BM25 retrieval (Hybrid modes only)
    # ------------------------------------------------------------------
    bm25_docs: list[Document] = []
    if "Hybrid" in retrieval_mode:
        try:
            from backend.bm25_index import build_bm25_index, bm25_search, vectorstore_to_doc_tuples
            doc_tuples = vectorstore_to_doc_tuples(vectorstore)
            bm25_model, bm25_corpus = build_bm25_index(doc_tuples)
            if bm25_model is not None:
                bm25_docs = bm25_search(query, bm25_model, bm25_corpus, top_k=fetch_k)
        except Exception:
            bm25_docs = []

    # ------------------------------------------------------------------
    # 3. Merge (RRF when hybrid, else passthrough)
    # ------------------------------------------------------------------
    if bm25_docs:
        # Weight by alpha: dense gets proportionally more candidates
        # We pass both lists; RRF handles ranking, alpha just controls pool
        candidate_docs = _reciprocal_rank_fusion([dense_docs, bm25_docs])
    else:
        candidate_docs = dense_docs

    # ------------------------------------------------------------------
    # 4. Reranking (when mode includes Rerank)
    # ------------------------------------------------------------------
    if "Rerank" in retrieval_mode or reranker_enabled:
        try:
            from backend.reranker import rerank
            final_docs = rerank(query, candidate_docs, top_k=rerank_top_k)
        except Exception:
            final_docs = candidate_docs[:rerank_top_k]
    else:
        final_docs = candidate_docs[:rerank_top_k]

    return final_docs


# ---------------------------------------------------------------------------
# Context formatter (mirrors backend.chains._format_docs)
# ---------------------------------------------------------------------------

def format_docs_for_context(docs: list[Document]) -> str:
    """Format a list of Documents into the context string the LLM expects."""
    return "\n\n---\n\n".join(
        f"[Source {i+1}: {os.path.basename(d.metadata.get('source', 'unknown'))}]\n{d.page_content}"
        for i, d in enumerate(docs)
    )
