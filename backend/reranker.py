"""
backend/reranker.py
--------------------
Cross-encoder reranker for Phase 2.

Wraps sentence-transformers CrossEncoder to re-score and re-order FAISS
retrieved documents.  The model is loaded once via @st.cache_resource and
reused across all requests.

This module is strictly additive — it imports nothing from existing backend
modules and is never imported by chains.py or vectorstore.py.

Default model: cross-encoder/ms-marco-MiniLM-L-6-v2
  - ~85 MB, no GPU required, ~5 ms per query on CPU for k=20 docs.
  - Scores are MS-MARCO relevance logits; higher = more relevant.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Model config
# ---------------------------------------------------------------------------

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_UNAVAILABLE_MSG = (
    "Reranker model not available — sentence-transformers may not be installed. "
    "Falling back to original retrieval order."
)


# ---------------------------------------------------------------------------
# Cached loader
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _load_cross_encoder():
    """Load CrossEncoder model once; returns None if library unavailable."""
    try:
        from sentence_transformers.cross_encoder import CrossEncoder  # type: ignore
        return CrossEncoder(RERANKER_MODEL)
    except ImportError:
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rerank(query: str, docs: list, top_k: int) -> list:
    """
    Re-score *docs* against *query* using the cross-encoder and return the
    top *top_k* documents ordered by descending relevance score.

    Falls back to returning the first *top_k* docs in the original order
    if the model is unavailable or scoring fails for any reason.
    """
    if not docs:
        return docs

    model = _load_cross_encoder()
    if model is None:
        st.sidebar.warning(_UNAVAILABLE_MSG)
        return docs[:top_k]

    try:
        pairs = [(query, doc.page_content) for doc in docs]
        scores = model.predict(pairs)
        scored = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]
    except Exception:
        return docs[:top_k]


def reranker_available() -> bool:
    """Return True if the cross-encoder loaded successfully."""
    return _load_cross_encoder() is not None
