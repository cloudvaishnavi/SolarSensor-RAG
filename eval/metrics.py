"""
eval/metrics.py
---------------
Pure-function metrics for the SolarSensor-RAG evaluation harness.
No imports from backend — all functions operate on plain Python data structures.

Phase 1 metrics:
  - Recall@K  (retrieval)
  - Faithfulness score  (LLM-as-judge, 0 or 1)
  - Answer relevance score  (LLM-as-judge, 0-3)
  - Refusal accuracy  (for adversarial questions)
"""

from __future__ import annotations

import os
import re
import time
from typing import Any

# ---------------------------------------------------------------------------
# Retrieval metrics
# ---------------------------------------------------------------------------

def recall_at_k(
    ideal_docs: list[str],
    retrieved_docs: list[Any],
    k: int,
) -> float:
    """
    Recall@K — returns 1.0 if at least one ideal source document appears
    in the top-k retrieved chunks, else 0.0.

    Parameters
    ----------
    ideal_docs      : list of expected source file basenames, e.g. ["01_dispatch_modes.txt"]
    retrieved_docs  : list of LangChain Document objects (have .metadata["source"])
    k               : cutoff (e.g. 5 or 10)
    """
    if not ideal_docs:
        # adversarial / no ideal doc — skip retrieval scoring
        return None  # type: ignore

    top_k = retrieved_docs[:k]
    retrieved_basenames = {
        os.path.basename(d.metadata.get("source", "")).lower()
        for d in top_k
    }
    ideal_set = {s.lower() for s in ideal_docs}
    return 1.0 if retrieved_basenames & ideal_set else 0.0


def aggregate_recall(per_question_recalls: list[float | None]) -> float:
    """Mean Recall@K across questions that have ideal docs (adversarial excluded)."""
    valid = [r for r in per_question_recalls if r is not None]
    if not valid:
        return 0.0
    return sum(valid) / len(valid)


# ---------------------------------------------------------------------------
# LLM-as-judge prompts
# ---------------------------------------------------------------------------

_FAITHFULNESS_PROMPT = """\
You are an evaluation judge for a grounded RAG system.

TASK: Determine whether the assistant's answer is fully supported by the retrieved context.

RETRIEVED CONTEXT:
{context}

QUESTION:
{question}

ASSISTANT ANSWER:
{answer}

SCORING RULES:
- Return 1 if EVERY factual claim in the answer is supported by the retrieved context above.
- Return 0 if the answer contains ANY claim not found in or contradicted by the context, \
or if the answer fabricates information not in the context.
- For answers that correctly say "I don't have enough information", return 1 (correct refusal is faithful).

Reply with ONLY the integer 0 or 1. No explanation.
"""

_RELEVANCE_PROMPT = """\
You are an evaluation judge for a question-answering system.

TASK: Score how directly and completely the answer addresses the question.

QUESTION:
{question}

ANSWER:
{answer}

SCORING RULES (0–3):
- 3 = Fully answers the question with correct, relevant details
- 2 = Mostly answers but misses a minor aspect or is partially complete
- 1 = Partially relevant but incomplete or off-topic in significant ways
- 0 = Does not answer the question at all, or completely off-topic

Reply with ONLY the integer 0, 1, 2, or 3. No explanation.
"""

_REFUSAL_PROMPT = """\
You are an evaluation judge for a grounded RAG system.

TASK: For an out-of-scope or adversarial question, determine whether the assistant \
correctly refused to answer (rather than hallucinating or guessing).

QUESTION:
{question}

ASSISTANT ANSWER:
{answer}

SCORING RULES:
- Return 1 if the assistant declined to answer, said it doesn't have enough information, \
or redirected the user to upload relevant documents.
- Return 0 if the assistant attempted to answer with any factual claim not grounded in the question context.

Reply with ONLY the integer 0 or 1. No explanation.
"""


# ---------------------------------------------------------------------------
# LLM judge helpers
# ---------------------------------------------------------------------------

def _extract_int(text: str, valid: set[int]) -> int | None:
    """Extract the first integer from an LLM response string."""
    for token in re.split(r"\s+", text.strip()):
        try:
            v = int(token)
            if v in valid:
                return v
        except ValueError:
            pass
    return None


def judge_faithfulness(
    question: str,
    context: str,
    answer: str,
    llm_callable,
) -> int:
    """
    Returns 1 (faithful) or 0 (unfaithful).
    llm_callable: a callable that takes a prompt string and returns a response string.
    """
    prompt = _FAITHFULNESS_PROMPT.format(
        context=context, question=question, answer=answer
    )
    for attempt in range(3):
        try:
            resp = llm_callable(prompt)
            score = _extract_int(resp, {0, 1})
            if score is not None:
                return score
        except Exception:
            time.sleep(5 * (attempt + 1))
    return 0  # fail-safe: mark as unfaithful on error


def judge_relevance(
    question: str,
    answer: str,
    llm_callable,
) -> int:
    """
    Returns 0, 1, 2, or 3.
    llm_callable: a callable that takes a prompt string and returns a response string.
    """
    prompt = _RELEVANCE_PROMPT.format(question=question, answer=answer)
    for attempt in range(3):
        try:
            resp = llm_callable(prompt)
            score = _extract_int(resp, {0, 1, 2, 3})
            if score is not None:
                return score
        except Exception:
            time.sleep(5 * (attempt + 1))
    return 0  # fail-safe


def judge_refusal(
    question: str,
    answer: str,
    llm_callable,
) -> int:
    """
    Returns 1 (correctly refused) or 0 (failed to refuse).
    Only used for adversarial category questions.
    """
    prompt = _REFUSAL_PROMPT.format(question=question, answer=answer)
    for attempt in range(3):
        try:
            resp = llm_callable(prompt)
            score = _extract_int(resp, {0, 1})
            if score is not None:
                return score
        except Exception:
            time.sleep(5 * (attempt + 1))
    return 0  # fail-safe


# ---------------------------------------------------------------------------
# Aggregate summary helpers
# ---------------------------------------------------------------------------

def compute_summary(results: list[dict]) -> dict:
    """
    Given a list of per-question result dicts produced by runner.py,
    compute aggregate metrics for the full eval set.
    """
    factual_synthesis = [r for r in results if r["category"] in ("factual", "synthesis")]
    adversarial = [r for r in results if r["category"] == "adversarial"]

    recall5_vals = [r["recall_at_5"] for r in factual_synthesis if r.get("recall_at_5") is not None]
    recall10_vals = [r["recall_at_10"] for r in factual_synthesis if r.get("recall_at_10") is not None]
    faith_vals = [r["faithfulness"] for r in results if r.get("faithfulness") is not None]
    relev_vals = [r["relevance"] for r in results if r.get("relevance") is not None]
    refusal_vals = [r["refusal_correct"] for r in adversarial if r.get("refusal_correct") is not None]

    def safe_mean(lst):
        return round(sum(lst) / len(lst), 4) if lst else None

    return {
        "total_questions": len(results),
        "factual_synthesis_count": len(factual_synthesis),
        "adversarial_count": len(adversarial),
        "recall_at_5": safe_mean(recall5_vals),
        "recall_at_10": safe_mean(recall10_vals),
        "faithfulness_mean": safe_mean(faith_vals),
        "faithfulness_pct": round(safe_mean(faith_vals) * 100, 1) if safe_mean(faith_vals) is not None else None,
        "relevance_mean": safe_mean(relev_vals),
        "relevance_pct": round(safe_mean(relev_vals) / 3.0 * 100, 1) if safe_mean(relev_vals) is not None else None,
        "refusal_accuracy": safe_mean(refusal_vals),
        "refusal_accuracy_pct": round(safe_mean(refusal_vals) * 100, 1) if safe_mean(refusal_vals) is not None else None,
    }
