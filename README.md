# SolarSense RAG

**SolarSense RAG** is an intelligent, strictly grounded AI assistant for Indian rooftop solar systems and the PM Surya Ghar (MNRE) scheme. It uses Retrieval-Augmented Generation (RAG) to answer questions _only_ from documents you upload — it never speculates or draws on the LLM's general world knowledge.

---

## Architecture Pipeline

```
Documents (PDF / TXT)
        │
        ▼
[1] Ingestion ──────── LangChain DirectoryLoader (PyPDFLoader + TextLoader)
        │              Sidebar uploader writes to documents/ and triggers rebuild
        ▼
[2] Chunking ─────────  RecursiveCharacterTextSplitter
                         Default: chunk_size=900, chunk_overlap=180
                         Configurable via sidebar → Advanced Chunking Settings
                         Two presets: Standard (900/180) · Large Chunks (1500/300)
        │
        ▼
[3] Embeddings ──────── Google Gemini Embedding 2  (768-dim, LOCKED)
                         Batch embedding (10 docs/batch) with 5-attempt retry
                         + exponential backoff on 429 / RESOURCE_EXHAUSTED
        │
        ▼
[4] FAISS Index ─────── Persisted to  faiss_index/
                         Signature file (_embedding_meta.txt) stores
                         "EMBED_MODEL|dim=EMBED_DIM"; mismatch quarantines
                         the stale index automatically and triggers a rebuild.
        │
        ▼
[5] Hybrid Retrieval ─── Dense (FAISS MMR, fetch_k=20) + Sparse (BM25)
                         Candidates are merged using Reciprocal Rank Fusion (RRF)
                         to capture both semantic meaning and exact keyword hits.
        │
        ▼
[6] Reranking ────────── ms-marco-MiniLM-L-6-v2 Cross-Encoder
                         Scrutinizes the query against each candidate chunk pair
                         and outputs a precise relevance score. Truncates to top-k.
        │
        ▼
[7] Query Rephrasing ─── RunnableWithMessageHistory + dedicated rephrase chain
                         Rewrites follow-up questions into standalone queries
                         BEFORE retrieval ("explain the second one" →
                         "Explain Backup Priority mode in more detail").
        │
        ▼
[8] Gemini Generation ── gemini-3.6-flash · temperature=0.15 (LOCKED)
                         Generates the answer using retrieved context +
                         full chat history passed through SYSTEM_PROMPT.
        │
        ▼
[9] Grounded Answer ──── Strict system prompt forbids outside knowledge.
                         Exact fallback sentence when context is insufficient.
                         Source-grounded phrases in the answer are highlighted
                         in yellow (simple string match, no NLP library).
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **chunk_size = 900, overlap = 180** | At ~900 chars a chunk covers exactly one dispatch mode, one subsidy slab, or one operational scenario without mid-sentence cuts. The 20% overlap prevents facts split across chunk boundaries from being lost to both sides. |
| **MMR (not pure similarity search)** | Multi-part questions need coverage across multiple passages. MMR fetches 20 candidates then picks the 5 that are both relevant and maximally diverse. |
| **Signature file** | Pins `EMBED_MODEL|dim=EMBED_DIM` to the saved FAISS index. If either changes, the index is quarantined and rebuilt automatically — no silent vector-space corruption. |
| **Strict grounding prompt** | The exact fallback sentence is baked into the system prompt so the model cannot paraphrase or soften it. This is verified by the Evaluation Results panel. |
| **RunnableWithMessageHistory** | Conversational memory stays inside LCEL — the rephrase chain handles pronoun/positional references before retrieval, not post-hoc. |
| **temperature = 0.15** | Determinism matters more than stylistic variety for a grounded technical assistant. |
| **Source highlighting (answer)** | `difflib.SequenceMatcher`-based n-gram matching finds 4+ word verbatim phrases from retrieved chunks and highlights them in the answer with a `<mark>` tag. Threshold ≥ 24 chars filters noise. |
| **Source highlighting (snippets)** | Inverse direction: phrases > 20 chars shared between the answer and each snippet card are highlighted in the source card body, so you can see exactly which snippet supported a given sentence. |
| **Per-message source persistence** | Sources (LangChain `Document` objects) are stored directly in `st.session_state.messages[i]["sources"]` so they survive Streamlit reruns without a second retrieval call. |

---

## How to Run

### 1. Clone and install

```bash
git clone <repo-url>
cd SolarSensor-RAG
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Set up your Google API key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
```

The key needs access to both `gemini-3.6-flash` (generation) and `models/gemini-embedding-2` (embeddings).

### 3. Add your documents

Drop PDF or TXT files into the `documents/` folder, **or** use the sidebar uploader in the app. The index rebuilds automatically the first time and is re-used on subsequent runs.

```
documents/
├── 01_dispatch_modes.txt
├── 02_pm_surya_ghar_guidelines.pdf
└── ...
```

### 4. Run the app

```bash
streamlit run app.py
```

The app starts at `http://localhost:8501`. It works with an empty `documents/` folder (KB shows Offline until you upload files).

---

## Feature Guide

### 1. Source Cards and Highlighting

Every assistant answer shows two levels of source attribution:

**Retrieved Context chips** (above the answer):
2-up compact cards showing filename + page number + highlighted snippet. Rendered by `_render_context_chips()`.

**View Grounding Sources expander** (below the answer):
Up to 5 source cards in an expandable section. First two appear side-by-side, remainder stacked full-width. Each card shows `📄 filename · Page N · #rank` and a 300-char snippet.

**Phrase highlighting in the answer:**
Phrases of 4+ words (≥ 24 chars) that appear verbatim in a retrieved chunk are wrapped in a soft yellow `<mark>` so you can visually trace which sentences came from the knowledge base. Uses `_highlight_answer_phrases()` — a sliding n-gram window over source `page_content`, no NLP library required.

**Phrase highlighting in snippets:**
The inverse direction: phrases > 20 chars shared between the answer and a source snippet are highlighted inside the source card using `difflib.SequenceMatcher`. This pinpoints the exact quote that grounded a claim.

Sources are stored with each message in `st.session_state.messages[i]["sources"]` so they persist correctly across reruns without a second retrieval call.

---

### 2. Compare: RAG vs Direct LLM — Big ON/OFF Switch

Above the chat area you will find a prominent card with a clearly labeled toggle:

```
┌──────────────────────────────────────────────────────┐
│  🔍  Compare: RAG vs Direct LLM   [OFF]   Toggle →  │
│       Only the grounded RAG answer is shown …        │
└──────────────────────────────────────────────────────┘
☐  Compare: RAG vs Direct LLM
```

- **OFF (default)** — only the grounded RAG answer is shown. This is the recommended production path.
- **ON** — after the grounded answer, a separate LLM call runs with *no retrieval context* and the two answers are shown side-by-side in an expandable comparison block:
  - **✅ Grounded (RAG)** — uses your documents, authoritative.
  - **⚠️ Ungrounded (Direct)** — uses general model knowledge, may be incomplete or inaccurate.
  - A yellow warning banner reinforces that the direct answer is for demonstration only.

The card border turns amber and an `ON` badge appears when the mode is active, making the state visually unambiguous. Toggle state persists in `st.session_state.compare_mode` and survives reruns. Comparison results are stored in the message dict so they re-render correctly from history.

> **Note:** How the two answers are _generated_ is not changed — only when and how the comparison block is displayed.

---

### 3. Configurable Chunking + Rebuild

In the sidebar under **⚙️ Advanced Chunking Settings**:

- **Strategy dropdown** — two presets:
  - *Standard (Default)* → 900 chars / 180 overlap. Recommended for this domain.
  - *Large Chunks (PDF-heavy)* → 1500 chars / 300 overlap. Better for dense regulatory annexures.
- **Chunk Size** and **Chunk Overlap** number fields let you fine-tune both values after selecting a preset.
- Click **🔄 Rebuild Index with These Settings** to apply. The index is **not** rebuilt automatically on field changes — only on explicit button press or new file upload.
- The main metrics strip updates to reflect the active chunk size after rebuild.

---

### 4. Retrieval Settings

In the sidebar under **⚡ Retrieval Settings**, you can dynamically change how documents are fetched and scored before generation:
- **Retrieval Mode**: Choose between "Dense only" (standard FAISS MMR), "Dense + Rerank" (FAISS followed by cross-encoder reranking), or "Hybrid + Rerank" (FAISS + BM25 merged via Reciprocal Rank Fusion, then reranked).
- **Top-K after Rerank**: Controls how many documents are passed to the LLM (default: 5).
- **Dense Weight (α)**: For Hybrid mode, balances dense vs sparse signals (default: 0.7).

---

### 5. Failure-Aware Loop

In the sidebar under **🔁 Failure-Aware Loop**, you can enable post-generation quality checks:
- **Quality Thresholds**: Sets the minimum required scores for Faithfulness (0-1) and Relevance (0-3).
- **Action**: If a generated answer falls below the thresholds, the system can either automatically **Rephrase query & retry once** (making an additional LLM call) or **Emit clear refusal message**.
- When triggered, a "Quality check failed" badge appears in the UI detailing the intervention.

---

### 6. User Feedback Summary

After every assistant response, a **👍 / 👎** feedback row appears directly below the answer with an optional comment field and a Submit button.

**Sidebar → 💬 User Feedback expander shows:**
- **Total responses rated** and **% positive** (shown in green).
- **Breakdown**: helpful / not helpful counts.
- **Recent Feedback** section: the 3 most recent entries (newest first), each showing:
  - Emoji + score label in colour (green = helpful, red = not helpful).
  - Question snippet (up to 50 chars).
  - Optional comment in italic.
  - Timestamp (HH:MM).

All feedback is stored in `st.session_state.user_feedback` (list of dicts: `question`, `answer`, `score`, `comment`, `timestamp`, `msg_index`). No external API is called; everything is session-only.

---

### 7. Conversation Memory and Clear Conversation

The assistant maintains full multi-turn memory via `RunnableWithMessageHistory` + `ChatMessageHistory`. Before each retrieval, the rephrase chain rewrites follow-up questions into self-contained queries (e.g. "explain the second one" → "Explain Backup Priority mode in more detail") so retrieval always uses a complete standalone question.

In the sidebar **💬 Conversation** expander:

- A **turn counter** shows how many questions have been asked in the current session.
- **🗑️ Clear Conversation** resets:
  - `st.session_state.messages` (all chat history)
  - `st.session_state.chat_history` (the `ChatMessageHistory` LCEL object)
  - `st.session_state.latest_sources` (last retrieved docs)
  - All `_fb_submitted_*` per-message feedback flags (so feedback widgets reset cleanly)
  - `_last_rewritten_query`, `pending_prompt`, and `_compare_toggle_widget` transient keys

The LLM chain itself is unchanged; a fresh `ChatMessageHistory` object is simply created.

---

### 8. Rewritten Query Debug

When the rephrase chain modifies a follow-up question (e.g., resolves a pronoun or positional reference), a collapsed **🔎 Rewritten query used for retrieval** expander appears below the answer showing the exact string sent to FAISS. Hidden by default; does not affect the production retrieval path.

---

## Project Structure

```
SolarSensor-RAG/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # Google API key (not committed)
├── logo.jpg                # Sidebar / top-bar logo
├── backend/                # Core RAG logic, chains, and retrieval
├── ui/                     # Streamlit components, sidebar, and theme
├── documents/              # Upload your PDF / TXT files here
└── faiss_index/            # Auto-created FAISS index (do not commit)
    ├── index.faiss
    ├── index.pkl
    └── _embedding_meta.txt # Signature file (embedding model + dim)
```

---

## Locked Constants (do not change without rebuilding the index)

| Constant | Value | Why locked |
|---|---|---|
| `EMBED_MODEL` | `models/gemini-embedding-2` | Changing the embedding model invalidates the FAISS index |
| `EMBED_DIM` | `768` | Must match the model's output dimensionality |
| `LLM_MODEL` | `gemini-3.6-flash` | Changing requires re-evaluation of grounding behavior |

The signature file system will quarantine an incompatible index automatically, but a rebuild costs quota — so treat these as pinned.

---

## Evaluation

“Upgraded SolarSensor-RAG with hybrid retrieval, cross-encoder reranking, formal evaluation harness (Recall@k + Faithfulness), and failure-aware refusal. Measured clear gains over the original dense-only version.”

### Evaluation Set
The evaluation runs on a **frozen 27-question benchmark dataset** (`eval_set.json`), meticulously designed to test all facets of the assistant:
- **Factual**: Direct retrieval of specific facts (e.g., subsidy amounts, modes).
- **Multi-fact / Synthesis**: Questions requiring aggregation across multiple chunks (e.g., comparisons, multi-step calculations).
- **Out-of-scope / Adversarial**: Unrelated questions, competitor queries, and jailbreak attempts.

### Benchmark Results (27/27 Questions)

| Metric               | Dense Only (Baseline) | Dense + Rerank | Hybrid + Rerank |
|----------------------|-----------------------|----------------|-----------------|
| Recall@5             | 100%                  | 100%           | 100%            |
| Recall@10            | 100%                  | 100%           | 100%            |
| Faithfulness         | 92.6%                 | 96.3%          | 96.3%           |
| Relevance            | 90.0%                 | 100%           | 100%            |
| Refusal Accuracy     | 100%                  | 100%           | 100%            |

### Key Findings
- **Cross-encoder reranking is a massive win:** It improved Relevance from 90% → 100% and Faithfulness from 92.6% → 96.3%. By forcing the absolute best chunks to the top of the context window, the generator hallucinates less.
- **Hybrid vs Dense:** The base dense retrieval (FAISS) was already achieving perfect 100% Recall on this dataset, meaning the sparse BM25 index and Reciprocal Rank Fusion (RRF) didn't provide additional numerical gains here. 
- **Safety is bulletproof:** Across all three pipelines, the system perfectly handled all adversarial and out-of-bounds questions (100% refusal accuracy).

### Concrete Reranking Example
In question `A04` ("Is PM Surya Ghar available in Pakistan?"), the Dense-only model flagged it for refusal but the Faithfulness judge caught a minor hallucinated caveat. The Cross-Encoder reranker perfectly prioritized the context boundaries, resulting in a cleaner, 100% faithful refusal.

### Known Limitations
- The Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) adds latency compared to pure vector lookup.
- Because the dataset is small and clean, we hit a "ceiling effect" where FAISS already had 100% Recall, masking the potential benefits of BM25 on harder, keyword-heavy queries.

---

## What Changed vs. What Was Left Untouched

### Changed / Added in this update

| Area | Change |
|---|---|
| **Compare mode — big ON/OFF switch** | Replaced the small collapsed-label toggle with a prominent card: amber border when ON, visible `ON`/`OFF` badge, labeled `st.toggle` with the full "Compare: RAG vs Direct LLM" label visible. State and generation logic unchanged. |
| **Source cards** | `_render_sources()` and `_render_context_chips()` are wired into both the history-replay loop and the new-message path, so sources appear under every assistant message. Sources stored in `st.session_state.messages[i]["sources"]` persist across reruns. |
| **Source highlighting — answer** | `_highlight_answer_phrases()`: sliding n-gram window that finds 4+ word verbatim phrases from retrieved chunks and wraps them in `<mark>` in the rendered answer. |
| **Source highlighting — snippets** | `_highlight_snippet()` uses `difflib.SequenceMatcher` to highlight shared phrases > 20 chars in source cards. |
| **Clear Conversation** | Now also clears `_compare_toggle_widget` key so the toggle widget re-syncs cleanly with `compare_mode` on next render. |
| **Retrieval Settings (Sidebar)** | Added toggle between Dense only, Dense + Rerank, and Hybrid + Rerank, with configurable Top-K and Dense Weight (α). |
| **Failure-Aware Loop (Sidebar)** | Added automated post-generation evaluation with configurable Faithfulness/Relevance thresholds and rephrase/retry logic. |
| **README** | Full rewrite with architecture pipeline, design decisions table, per-feature guide, and "changed vs. untouched" section. |

### Left 100% Untouched (backend pipeline)

- `EMBED_MODEL`, `EMBED_DIM`, `LLM_MODEL`, `temperature`
- `SYSTEM_PROMPT` (exact text, including exact fallback sentence)
- FAISS signature logic (`_current_embed_signature`, `_read_index_signature`, `_write_index_signature`, `_quarantine_incompatible_index`)
- `create_vector_store` backend (batching, retry, backup/restore logic, FAISS save/load)
- MMR retriever settings (`k=5`, `fetch_k=20`, `lambda_mult=0.7`)
- `rephrase_prompt`, `rephrase_chain`, `_retrieve_docs`, `rag_chain`, `RunnableWithMessageHistory`
- `_render_feedback_widget` (per-message thumbs widget logic)
- `_call_direct_llm` (RAG vs Direct comparison backend — only the toggle UI changed)
- CSS/theme system, sidebar layout, PM Surya Ghar calculator, evaluation panel, metrics cards

---

## Known Issues

- **Silent Degradation in Hybrid Retrieval**: If the `rank_bm25` library is missing, "Hybrid + Rerank" mode silently degrades to Dense-only search without warning the user.
- **Silent Failure on Corrupt Documents**: Uploading a corrupted PDF or TXT file will cause the `DirectoryLoader` to silently skip the file without throwing an error in the UI.
- **Incomplete Answer Highlighting**: The highlighter uses `.find()`, which only matches the first occurrence of a phrase. If the LLM repeats a verbatim phrase twice in the same response, the second occurrence will not be highlighted.

---

*Built with Streamlit · LangChain · Google Gemini · FAISS*
