import os
import shutil
import streamlit as st
from backend.vectorstore import DOCS_FOLDER, INDEX_PATH, EMBED_MODEL, EMBED_DIM

def render_upload_page(vectorstore, doc_count: int, doc_names: list, T: dict):
    """
    Renders the approved Stitch Document Ingestion & Indexing Pipeline screen (Screen ID: 033df50c783a4b848754b57d5b850ff9).
    Preserves all existing upload handlers, backup logic, and cache invalidation.
    """
    kb_online = vectorstore is not None
    chunk_sz = st.session_state.get("chunk_size", 900)
    chunk_ov = st.session_state.get("chunk_overlap", 180)

    st.markdown(f"""
<div class="stitch-page-wrap">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
        <span style="font-size:0.75rem;font-weight:700;padding:3px 10px;border-radius:9999px;background:{'rgba(8,127,91,0.12)' if kb_online else 'rgba(239,68,68,0.12)'};color:{'#087F5B' if kb_online else '#EF4444'};">
            ● FAISS Vector Store: {'Online' if kb_online else 'Offline'}
        </span>
        <span style="font-size:0.72rem;color:{T['text_dim']};">&bull; {doc_count} documents indexed</span>
    </div>
    <div class="stitch-page-title-row">
        <div>
            <h1 class="stitch-page-title">Document Ingestion & Indexing Pipeline</h1>
            <p class="stitch-page-desc">
                Upload official rooftop solar policies, scheme guidelines, technical datasheets, or tariff PDFs/TXTs to expand the SolarSense RAG knowledge base.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # 2-Column Responsive Layout: Left Upload Zone + Right Ingestion Specs
    # ----------------------------------------------------------------
    left_col, right_col = st.columns([65, 35], gap="large")

    with left_col:
        # Styled Upload Card (Highlighted)
        st.markdown(f"""
<div class="stitch-card" style="border:2px dashed #087F5B;background:#FFFFFF;text-align:center;padding:32px 24px;margin-bottom:18px;border-radius:16px;box-shadow:0 1px 4px rgba(5,46,36,0.06);">
    <div style="width:54px;height:54px;border-radius:50%;background:#087F5B;color:#FFFFFF;display:inline-flex;align-items:center;justify-content:center;font-size:1.6rem;margin-bottom:12px;box-shadow:0 2px 8px rgba(8,127,91,0.25);">
        📤
    </div>
    <h3 style="font-size:1.25rem;font-weight:800;color:#052E24;margin-bottom:6px;letter-spacing:-0.01em;">Upload Solar Policy & Technical Documents</h3>
    <p style="font-size:0.84rem;color:#64756B;max-width:480px;margin:0 auto 16px auto;line-height:1.5;font-weight:500;">
        Drop your PDF or TXT files below. Ingestion will extract text, chunk with recursive character splitting, compute 768-dim embeddings, and update the FAISS index.
    </p>
    <div style="display:inline-flex;gap:8px;font-size:0.75rem;font-weight:700;color:#052E24;">
        <span style="background:#FFFFFF;border:1.5px solid #C9DCCF;padding:3px 10px;border-radius:8px;">📄 PDF, TXT</span>
        <span style="background:#FFFFFF;border:1.5px solid #C9DCCF;padding:3px 10px;border-radius:8px;">⚡ Max 200MB</span>
    </div>
</div>
""", unsafe_allow_html=True)

        # Reused Native Streamlit Uploader
        uploaded_files = st.file_uploader(
            "Select solar documents to ingest",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            key="page_doc_uploader",
            label_visibility="collapsed"
        )

        if uploaded_files:
            # Preservation of exact original ingestion flow
            with st.spinner(f"Saving {len(uploaded_files)} file(s) and refreshing knowledge base..."):
                for f in uploaded_files:
                    target_path = os.path.join(DOCS_FOLDER, f.name)
                    with open(target_path, "wb") as out:
                        out.write(f.getbuffer())

                if os.path.exists(INDEX_PATH):
                    backup_path = INDEX_PATH + "_backup"
                    if os.path.exists(backup_path):
                        shutil.rmtree(backup_path, ignore_errors=True)
                    shutil.move(INDEX_PATH, backup_path)

                st.cache_resource.clear()
                st.session_state.kb_loaded = False

            st.success(f"✅ Successfully uploaded {len(uploaded_files)} document(s). Index is rebuilding…")
            st.rerun()

        # Ingestion Buffer / Ingested Corpus Sample (Clean container, no empty box)
        with st.container(key="upload_corpus_card"):
            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
    <div>
        <h4 style="font-size:0.95rem;font-weight:700;color:{T['text']};margin:0;">Active Corpus Documents</h4>
        <div style="font-size:0.75rem;color:{T['text_muted']};margin-top:2px;">Currently indexed and available for retrieval</div>
    </div>
    <span style="font-size:0.72rem;font-weight:700;background:rgba(8,127,91,0.12);color:#087F5B;padding:3px 10px;border-radius:9999px;">
        {doc_count} Active
    </span>
</div>
""", unsafe_allow_html=True)

            # Show list of loaded documents
            if doc_names:
                rows = []
                for name in doc_names[:10]:
                    ext = "PDF" if name.lower().endswith(".pdf") else "TXT"
                    b_class = "format-badge-pdf" if ext == "PDF" else "format-badge-txt"
                    rows.append(f"""
<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 10px;border-bottom:1px solid {T['border_soft']};font-size:0.8rem;">
    <div style="display:flex;align-items:center;gap:8px;color:{T['text']};font-weight:600;">
        <span>📄</span>
        <span>{name}</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <span class="format-badge {b_class}">{ext}</span>
        <span style="font-size:0.72rem;color:#087F5B;font-weight:600;">● Active</span>
    </div>
</div>
""")
                st.markdown("".join(rows), unsafe_allow_html=True)
                if len(doc_names) > 10:
                    st.caption(f"Showing 10 of {len(doc_names)} documents. View all in Knowledge Base.")
            else:
                st.info("No documents currently in corpus. Upload above to initialize index.")

    with right_col:
        # Ingestion Parameters Card
        st.markdown(f"""
<div class="stitch-card">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <h4 style="font-size:0.92rem;font-weight:700;color:{T['text']};margin:0;">Ingestion Parameters</h4>
        <span style="font-size:0.7rem;font-weight:700;color:{T['text_dim']};background:{T['surface_alt']};padding:2px 8px;border-radius:6px;border:1px solid {T['border']};">Default Preset</span>
    </div>
    <div style="font-size:0.78rem;line-height:1.7;color:{T['text_muted']};">
        <b>Text Splitter:</b> RecursiveCharacterTextSplitter<br>
        <b>Chunk Size:</b> {chunk_sz} characters (~180-220 tokens)<br>
        <b>Chunk Overlap:</b> {chunk_ov} characters (context boundary)<br>
        <b>Embeddings:</b> {EMBED_MODEL} ({EMBED_DIM}d)
    </div>
    <div style="margin-top:12px;padding:8px 10px;background:{T['surface_alt']};border-radius:8px;font-size:0.72rem;color:{T['text_dim']};">
        💡 To adjust chunk size or overlap, visit <b>Settings & Advanced Retrieval</b>.
    </div>
</div>
""", unsafe_allow_html=True)

        # Quality Ingestion Checklist
        st.markdown(f"""
<div class="stitch-card">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <span style="font-size:1.1rem;">📋</span>
        <h4 style="font-size:0.92rem;font-weight:700;color:{T['text']};margin:0;">Quality Ingestion Checklist</h4>
    </div>
    <div style="display:flex;flex-direction:column;gap:10px;font-size:0.78rem;color:{T['text_muted']};line-height:1.45;">
        <div style="display:flex;align-items:flex-start;gap:8px;">
            <span style="color:#087F5B;font-weight:700;">✓</span>
            <div><b>Clean Text Formatting</b><br>Avoid heavy diagonal watermarks which corrupt tokenizer token sequences.</div>
        </div>
        <div style="display:flex;align-items:flex-start;gap:8px;">
            <span style="color:#087F5B;font-weight:700;">✓</span>
            <div><b>Standard Policy Tables Preserved</b><br>Ensure slab rate and tariff tables have readable grid boundaries or row alignments.</div>
        </div>
        <div style="display:flex;align-items:flex-start;gap:8px;">
            <span style="color:#087F5B;font-weight:700;">✓</span>
            <div><b>Discom & State Clearly Identified</b><br>Helps RAG disambiguate state net metering guidelines (e.g. MSEDCL vs BESCOM).</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        # Pipeline Flow Path Card
        st.markdown(f"""
<div style="background:{T['surface_subtle']};border:1px solid {T['border']};border-radius:12px;padding:12px;font-size:0.72rem;color:{T['text_dim']};line-height:1.5;">
    <b>Active Pipeline:</b> PyPDF / TextLoader &rarr; RecursiveTextSplitter({chunk_sz}, {chunk_ov}) &rarr; text-embedding-004 &rarr; FAISS Index (L2)
</div>
""", unsafe_allow_html=True)
