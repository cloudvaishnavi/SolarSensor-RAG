"""
backend/bm25_index.py
----------------------
BM25 keyword retrieval for Phase 3 Hybrid Retrieval.

Uses rank-bm25 (pure Python, no model download) to build an Okapi BM25 index
over the same document chunks that FAISS holds.  BM25 complements dense FAISS
retrieval by excelling at rare-keyword matching (e.g. exact scheme names,
section numbers, amounts like "₹78,000").

Additive module — not imported by any existing backend file.
"""

from __future__ import annotations

import re
import streamlit as st
from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# Simple tokeniser
# ---------------------------------------------------------------------------

def _tokenise(text: str) -> list[str]:
    """Lowercase + split on non-alphanumeric characters."""
    return re.findall(r"[a-z0-9₹]+", text.lower())


# ---------------------------------------------------------------------------
# Index builder (cached — built from live FAISS docstore)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def build_bm25_index(doc_tuples: tuple[tuple[str, str], ...]):
    """
    Build and cache a BM25Okapi index.

    *doc_tuples* is a tuple-of-tuples so it is hashable and can be used as a
    cache key.  Each inner tuple is (page_content, source_metadata).

    Returns (bm25_model, docs_list) or (None, []) if rank_bm25 is unavailable.
    """
    try:
        from rank_bm25 import BM25Okapi  # type: ignore
    except ImportError:
        return None, []

    if not doc_tuples:
        return None, []

    docs = [
        Document(page_content=content, metadata={"source": source})
        for content, source in doc_tuples
    ]
    tokenised_corpus = [_tokenise(doc.page_content) for doc in docs]
    bm25 = BM25Okapi(tokenised_corpus)
    return bm25, docs


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def bm25_search(query: str, bm25, docs: list, top_k: int) -> list[Document]:
    """
    Score all documents against *query* with BM25 and return the top *top_k*
    ordered by descending score.

    Returns [] if the index is None (library unavailable).
    """
    if bm25 is None or not docs:
        return []

    tokens = _tokenise(query)
    if not tokens:
        return docs[:top_k]

    scores = bm25.get_scores(tokens)
    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:top_k]]


# ---------------------------------------------------------------------------
# Helper: extract hashable doc tuples from a FAISS vectorstore
# ---------------------------------------------------------------------------

def vectorstore_to_doc_tuples(vectorstore) -> tuple[tuple[str, str], ...]:
    """
    Extract all document chunks from a LangChain FAISS vectorstore as a
    hashable tuple of (page_content, source) pairs for use as a cache key.
    """
    try:
        # FAISS stores docs in vectorstore.docstore._dict
        store_dict = vectorstore.docstore._dict
        result = tuple(
            (doc.page_content, doc.metadata.get("source", ""))
            for doc in store_dict.values()
            if hasattr(doc, "page_content")
        )
        return result
    except Exception:
        return ()
