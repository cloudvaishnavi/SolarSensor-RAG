import streamlit as st
import os
import time
import shutil
import re
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

DOCS_FOLDER = "documents"
INDEX_PATH  = "faiss_index"

# --------------------------------------------------
# Embedding model config (LOCKED — do not change)
# --------------------------------------------------
EMBED_MODEL = "models/gemini-embedding-2"
EMBED_DIM   = 768  # Google-recommended value (also valid: 1536, 3072)
LLM_MODEL   = "gemini-3.6-flash"

# --------------------------------------------------
# Embedding model config (LOCKED — do not change)
# --------------------------------------------------

# --------------------------------------------------
# Embedding index-signature helpers — BACKEND UNCHANGED
# --------------------------------------------------
def _parse_retry_delay(err_str, default=20):
    """Extract Google's suggested retry_delay (seconds) from the error text if present."""
    m = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', err_str)
    if m:
        return int(m.group(1)) + 2  # small buffer
    return default

_SIG_FILENAME = "_embedding_meta.txt"

def _current_embed_signature() -> str:
    return f"{EMBED_MODEL}|dim={EMBED_DIM}"

def _read_index_signature(index_path: str):
    sig_file = os.path.join(index_path, _SIG_FILENAME)
    if os.path.exists(sig_file):
        try:
            with open(sig_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return None
    return None

def _write_index_signature(index_path: str):
    sig_file = os.path.join(index_path, _SIG_FILENAME)
    try:
        with open(sig_file, "w", encoding="utf-8") as f:
            f.write(_current_embed_signature())
    except Exception:
        pass

# --------------------------------------------------
# Embedding index-signature helpers — BACKEND UNCHANGED
# --------------------------------------------------


def _quarantine_incompatible_index(index_path: str):
    if not os.path.exists(index_path):
        return
    stale_path = f"{index_path}_incompatible_{int(time.time())}"
    try:
        shutil.move(index_path, stale_path)
    except Exception:
        shutil.rmtree(index_path, ignore_errors=True)

# --------------------------------------------------
# Vector Store (cached to disk) — BACKEND UNCHANGED
# --------------------------------------------------

@st.cache_resource(show_spinner=False)
def create_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL, output_dimensionality=EMBED_DIM)
    documents  = []
    try:
        documents.extend(DirectoryLoader(DOCS_FOLDER, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"}).load())
    except Exception:
        pass
    try:
        documents.extend(DirectoryLoader(DOCS_FOLDER, glob="**/*.pdf", loader_cls=PyPDFLoader).load())
    except Exception:
        pass
    if not documents:
        return None, 0, []

    doc_names = sorted(set(os.path.basename(d.metadata.get("source", "unknown")) for d in documents))
    idx_file = os.path.join(INDEX_PATH, "index.faiss")

    if os.path.exists(idx_file) and _read_index_signature(INDEX_PATH) != _current_embed_signature():
        _quarantine_incompatible_index(INDEX_PATH)
        idx_file = os.path.join(INDEX_PATH, "index.faiss")

    if os.path.exists(idx_file):
        try:
            vs = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            return vs, len(documents), doc_names
        except Exception:
            pass

    # Rebuild only when index is missing / incompatible
    c_size = st.session_state.get("chunk_size", 900)
    c_overlap = st.session_state.get("chunk_overlap", 180)
    splitter = RecursiveCharacterTextSplitter(chunk_size=c_size, chunk_overlap=c_overlap, separators=["\n\n", "\n", ". ", " ", ""])
    splits = splitter.split_documents(documents)

    backup_path = INDEX_PATH + "_backup"
    BATCH_SIZE = 10
    SLEEP_BETWEEN_BATCHES = 3

    vs = None
    try:
        n_batches = (len(splits) + BATCH_SIZE - 1) // BATCH_SIZE
        for i in range(0, len(splits), BATCH_SIZE):
            batch = splits[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            last_err = None
            for attempt in range(5):
                try:
                    if vs is None:
                        vs = FAISS.from_documents(batch, embeddings)
                    else:
                        vs.add_documents(batch)
                    last_err = None
                    break
                except Exception as e:
                    last_err = str(e)
                    if "429" in last_err or "RESOURCE_EXHAUSTED" in last_err or "Quota" in last_err:
                        wait = _parse_retry_delay(last_err, default=20 * (attempt + 1))
                        time.sleep(wait)
                        continue
                    elif "500" in last_err or "503" in last_err or "INTERNAL" in last_err:
                        time.sleep(3)
                        continue
                    else:
                        raise

            if last_err is not None:
                raise RuntimeError(last_err)

            time.sleep(SLEEP_BETWEEN_BATCHES)

        vs.save_local(INDEX_PATH)
        _write_index_signature(INDEX_PATH)
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path, ignore_errors=True)
        return vs, len(documents), doc_names

    except Exception as e:
        err_str = str(e)
        # Try to fall back to previous good index
        if os.path.exists(backup_path) and _read_index_signature(backup_path) == _current_embed_signature():
            try:
                shutil.copytree(backup_path, INDEX_PATH, dirs_exist_ok=True)
                vs = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
                return vs, len(documents), doc_names
            except Exception:
                pass
        # If we have a partial index, save it
        if vs is not None:
            try:
                vs.save_local(INDEX_PATH)
                _write_index_signature(INDEX_PATH)
            except Exception:
                pass
        raise e

# --------------------------------------------------
