"""
backend/failure_loop.py
------------------------
Phase 4 – Failure-Aware Generation Loop.

After the primary answer is generated, this module:
  1. Scores faithfulness and relevance using lightweight LLM-as-judge calls.
  2. If the score is below threshold:
       (A) Rephrase query → retrieve fresh context → regenerate (one retry), OR
       (B) Emit a clear refusal message.
  3. Returns a structured result dict for display in the UI.

This module is strictly additive — it imports from backend.retrieval_pipeline
but not from backend.chains or backend.vectorstore.

Public API
----------
    score_answer(question, answer, context, llm_callable) -> ScoreResult
    run_failure_loop(question, answer, context, docs, vectorstore,
                     llm_callable, gen_callable, config) -> LoopResult

Types (plain dicts for simplicity)
------------------------------------
ScoreResult:
    faithfulness: int       0 or 1
    relevance:    int       0–3
    passed:       bool

LoopResult:
    original_answer:    str
    final_answer:       str
    triggered:          bool      True if loop fired (score was low)
    action:             str       "passed" | "rephrased" | "refused"
    score:              ScoreResult
    rephrased_query:    str | None
    reason:             str       Human-readable explanation shown in UI
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Judge prompts (deterministic, temperature=0)
# ---------------------------------------------------------------------------

_FAITHFULNESS_PROMPT = """\
You are a strict grounding evaluator. Given a QUESTION, a CONTEXT (retrieved from documents), and an ANSWER:

Respond with ONLY the digit 1 if the answer is fully supported by the context,
or ONLY the digit 0 if the answer contains claims not found in the context or contradicts it.

QUESTION: {question}
CONTEXT: {context}
ANSWER: {answer}

Your response (ONLY 0 or 1):"""

_RELEVANCE_PROMPT = """\
You are a relevance evaluator. Rate how well the ANSWER addresses the QUESTION on a 0–3 scale:

0 = Answer does not address the question at all.
1 = Answer is tangentially related but misses the core question.
2 = Answer partially addresses the question.
3 = Answer fully and directly addresses the question.

QUESTION: {question}
ANSWER: {answer}

Your response (ONLY a single digit 0, 1, 2, or 3):"""

_REPHRASE_PROMPT = """\
You are a query reformulation expert. The original question below yielded a poor-quality answer from a document retrieval system.

Reformulate the question to be more specific, using different keywords that might better match the relevant document sections.
Return ONLY the reformulated question — no explanation, no preamble.

Original question: {question}"""


# ---------------------------------------------------------------------------
# Score extraction helpers
# ---------------------------------------------------------------------------

def _extract_int(text: str, valid: set[int] = {0, 1}) -> int | None:
    """Extract the first integer from text that is in the valid set."""
    for ch in text.strip():
        if ch.isdigit():
            val = int(ch)
            if val in valid:
                return val
    return None


# ---------------------------------------------------------------------------
# Public: score_answer
# ---------------------------------------------------------------------------

def score_answer(
    question: str,
    answer: str,
    context: str,
    llm_callable,
) -> dict:
    """
    Score *answer* for faithfulness (0/1) and relevance (0–3).

    *llm_callable* is a function (prompt_str) -> str.
    Returns a ScoreResult dict.
    """
    # Faithfulness
    faith_prompt = _FAITHFULNESS_PROMPT.format(
        question=question, context=context, answer=answer
    )
    try:
        faith_raw = llm_callable(faith_prompt)
        faithfulness = _extract_int(faith_raw, {0, 1})
        if faithfulness is None:
            faithfulness = 1  # default to pass on parse failure
    except Exception:
        faithfulness = 1

    # Relevance
    relev_prompt = _RELEVANCE_PROMPT.format(question=question, answer=answer)
    try:
        relev_raw = llm_callable(relev_prompt)
        relevance = _extract_int(relev_raw, {0, 1, 2, 3})
        if relevance is None:
            relevance = 3  # default to pass
    except Exception:
        relevance = 3

    return {
        "faithfulness": faithfulness,
        "relevance": relevance,
        "passed": True,   # filled in by caller with thresholds
    }


# ---------------------------------------------------------------------------
# Public: run_failure_loop
# ---------------------------------------------------------------------------

def run_failure_loop(
    question: str,
    answer: str,
    context: str,
    docs: list,
    vectorstore,
    llm_callable,
    gen_callable,
    config: dict,
) -> dict:
    """
    Run the failure-aware loop.

    Parameters
    ----------
    question      : Original (possibly rephrased-by-chain) question.
    answer        : Answer from primary generation.
    context       : Context string used for primary generation.
    docs          : Retrieved docs used for primary generation.
    vectorstore   : Live FAISS store (for re-retrieval on rephrase path).
    llm_callable  : (prompt_str) -> str  — lightweight judge LLM.
    gen_callable  : (question, context) -> str  — generation LLM.
    config        : dict with keys:
                      faith_threshold  int  (default 1)
                      relev_threshold  int  (default 2)
                      loop_action      str  "rephrase" | "refuse"
                      retrieval_mode   str  forwarded to retrieve()
                      reranker_enabled bool
                      rerank_top_k     int
                      hybrid_alpha     float

    Returns a LoopResult dict.
    """
    faith_threshold = config.get("faith_threshold", 1)
    relev_threshold = config.get("relev_threshold", 2)
    loop_action     = config.get("loop_action", "rephrase")

    # Step 1: score primary answer
    score = score_answer(question, answer, context, llm_callable)
    passed = (
        score["faithfulness"] >= faith_threshold
        and score["relevance"] >= relev_threshold
    )
    score["passed"] = passed

    if passed:
        return {
            "original_answer": answer,
            "final_answer": answer,
            "triggered": False,
            "action": "passed",
            "score": score,
            "rephrased_query": None,
            "reason": (
                f"Answer passed quality checks "
                f"(faithfulness={score['faithfulness']}, relevance={score['relevance']})."
            ),
        }

    # Step 2: loop triggered
    reason_parts = []
    if score["faithfulness"] < faith_threshold:
        reason_parts.append(f"faithfulness={score['faithfulness']} < threshold {faith_threshold}")
    if score["relevance"] < relev_threshold:
        reason_parts.append(f"relevance={score['relevance']} < threshold {relev_threshold}")
    low_score_reason = "Low quality: " + " · ".join(reason_parts)

    if loop_action == "refuse":
        return {
            "original_answer": answer,
            "final_answer": (
                "I don't have enough information in the loaded documents to answer that accurately. "
                "Please upload the relevant document or rephrase your question."
            ),
            "triggered": True,
            "action": "refused",
            "score": score,
            "rephrased_query": None,
            "reason": low_score_reason,
        }

    # Step 3: rephrase + retry
    rephrased_query = question
    try:
        rephrase_prompt = _REPHRASE_PROMPT.format(question=question)
        rephrased_query = llm_callable(rephrase_prompt).strip()
        if not rephrased_query:
            rephrased_query = question
    except Exception:
        pass

    # Re-retrieve with rephrased query
    try:
        from backend.retrieval_pipeline import retrieve, format_docs_for_context
        new_docs = retrieve(
            query=rephrased_query,
            vectorstore=vectorstore,
            retrieval_mode=config.get("retrieval_mode", "Dense only"),
            reranker_enabled=config.get("reranker_enabled", False),
            rerank_top_k=config.get("rerank_top_k", 5),
            hybrid_alpha=config.get("hybrid_alpha", 0.7),
        )
        new_context = format_docs_for_context(new_docs)
    except Exception:
        new_context = context

    # Re-generate
    try:
        new_answer = gen_callable(rephrased_query, new_context)
    except Exception:
        new_answer = answer

    return {
        "original_answer": answer,
        "final_answer": new_answer,
        "triggered": True,
        "action": "rephrased",
        "score": score,
        "rephrased_query": rephrased_query,
        "reason": low_score_reason,
    }
