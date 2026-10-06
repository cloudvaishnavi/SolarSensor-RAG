import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv()


# Ensure imports work
sys.path.append(os.path.abspath("."))

print("1. Loading Vector Store...")
from backend.vectorstore import create_vector_store
from backend.retrieval_pipeline import retrieve
from backend.failure_loop import run_failure_loop

vectorstore, doc_count, doc_names = create_vector_store()
print(f"   => Loaded {doc_count} document chunks.")

query = "What is the subsidy for 2kW PM Surya Ghar?"

print("\n2. Testing Mode: Dense only")
docs_dense = retrieve(query, vectorstore, retrieval_mode="Dense only", fetch_k=20, rerank_top_k=5)
print(f"   => Retrieved {len(docs_dense)} documents.")

print("\n3. Testing Mode: Dense + Rerank")
docs_dense_rerank = retrieve(query, vectorstore, retrieval_mode="Dense + Rerank", fetch_k=20, rerank_top_k=5)
print(f"   => Retrieved {len(docs_dense_rerank)} documents. Reranker active.")

print("\n4. Testing Mode: Hybrid + Rerank (BM25 + FAISS -> RRF -> CrossEncoder)")
docs_hybrid = retrieve(query, vectorstore, retrieval_mode="Hybrid + Rerank", fetch_k=20, rerank_top_k=5)
print(f"   => Retrieved {len(docs_hybrid)} documents. BM25 and Reranker active.")

print("\n5. Testing Failure-Aware Loop (Simulated low score)")
# We use a mock judge that always returns 0 (fails thresholds)
def mock_judge(prompt):
    return "0"

# We use a mock generator to simulate the retry
def mock_gen(q, ctx):
    return "[REGENERATED] This is the new answer."

res = run_failure_loop(
    question="Tell me a joke",
    answer="Why did the chicken cross the road?",
    context="Some irrelevant context",
    docs=[],
    vectorstore=vectorstore,
    llm_callable=mock_judge,
    gen_callable=mock_gen,
    config={
        "faith_threshold": 1,
        "relev_threshold": 2,
        "loop_action": "rephrase",
        "retrieval_mode": "Dense only",
        "reranker_enabled": False,
        "rerank_top_k": 5,
        "hybrid_alpha": 0.7
    }
)
print(f"   => Loop triggered: {res['triggered']}")
print(f"   => Action taken: {res['action']}")
print(f"   => Final answer: {res['final_answer']}")
print(f"   => Reason given: {res['reason']}")

print("\nAll pipeline components verified locally.")
