import streamlit as st
import os
from backend.text_utils import img_to_b64


def render_sidebar(vectorstore, doc_count: int, doc_names: list, T: dict, LOGO_PATH: str):
    """
    Renders the approved Google Stitch navigation sidebar.
    Keeps only:
      1. SolarSense branding and logo
      2. The eight functional navigation destinations
      3. A compact knowledge-base status indicator
      4. A small, tasteful clean-energy branding card
      5. A restrained version/technology footer

    All duplicate controls have been relocated to their dedicated pages.
    """
    with st.sidebar:
        # ----------------------------------------------------------------
        # 1. SolarSense Brand & Logo Header
        # ----------------------------------------------------------------
        logo_b64 = img_to_b64(LOGO_PATH) if os.path.exists(LOGO_PATH) else ""
        if logo_b64:
            logo_img_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width:38px;height:38px;border-radius:10px;object-fit:cover;" />'
        else:
            logo_img_html = f'<div class="sidebar-logo-icon">☀️</div>'

        st.markdown(
            f"""
<div class="sidebar-logo-wrap">
    {logo_img_html}
    <div>
        <div class="sidebar-logo-name">SolarSense</div>
        <div class="sidebar-logo-sub">Rooftop Solar AI Assistant</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------------------
        # 2. Eight Functional Navigation Destinations (Stitch Nav Deck)
        # ----------------------------------------------------------------
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Chat Assistant"

        NAV_PAGES = [
            ("Chat Assistant", "💬", "chat_assistant"),
            ("Knowledge Base", "📁", "knowledge_base"),
            ("Upload Documents", "📤", "upload_docs"),
            ("Solar Calculator", "🧮", "solar_calc"),
            ("Evaluation & Results", "📊", "eval_results"),
            ("Settings & Advanced Retrieval", "⚙️", "settings"),
            ("System Status & Architecture", "🏛️", "system_status"),
            ("Example Questions", "💡", "example_questions"),
        ]

        with st.container(key="stitch_nav_deck"):
            for page_name, icon, page_key in NAV_PAGES:
                is_active = (st.session_state.current_page == page_name)
                if st.button(
                    f"{icon}  {page_name}",
                    key=f"nav_btn_{page_key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    if st.session_state.current_page != page_name:
                        st.session_state.current_page = page_name
                        st.session_state["_last_query_page"] = page_name
                        st.query_params["page"] = page_name
                        st.rerun()

        st.markdown('<div style="height:4px;border-bottom:1px solid rgba(255, 255, 255, 0.12);margin:8px 0 10px 0;"></div>', unsafe_allow_html=True)
        if st.button("🌐  Public Home / Sign Out", key="nav_btn_public_landing", use_container_width=True):
            from ui.auth_service import sign_out
            sign_out()
            st.query_params["page"] = "landing"
            st.rerun()

        # Display user authentication badge if logged in
        if st.session_state.get("authenticated"):
            u_name = st.session_state.get("user_name", "")
            is_preview = st.session_state.get("preview_mode", False)
            if is_preview:
                st.markdown(
                    '<div style="font-size:0.72rem;font-weight:700;color:#A3E635;background:rgba(8, 127, 91, 0.35);border:1px solid rgba(163, 230, 53, 0.35);border-radius:6px;padding:3px 8px;margin-bottom:8px;text-align:center;">'
                    '⚡ Demo Mode</div>',
                    unsafe_allow_html=True,
                )
            elif u_name:
                st.markdown(
                    f'<div style="font-size:0.72rem;color:#E2ECE7;background:rgba(255, 255, 255, 0.10);border:1px solid rgba(255, 255, 255, 0.18);border-radius:6px;padding:3px 8px;margin-bottom:8px;text-align:center;">'
                    f'👤 {u_name}</div>',
                    unsafe_allow_html=True,
                )

        # ----------------------------------------------------------------
        # 3. Compact Knowledge Base Status Indicator
        # ----------------------------------------------------------------
        if vectorstore is not None:
            st.markdown(
                f'<div class="info-row" style="margin-bottom:12px;"><span class="info-dot info-dot-on"></span>Knowledge Base Live &middot; {doc_count} doc(s)</div>',
                unsafe_allow_html=True,
            )
        elif doc_count > 0:
            st.markdown(
                f'<div class="info-row" style="margin-bottom:12px;"><span class="info-dot info-dot-off"></span>Offline &mdash; indexing failed, please retry</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="info-row" style="margin-bottom:12px;"><span class="info-dot info-dot-off"></span>Offline &mdash; no documents yet</div>',
                unsafe_allow_html=True,
            )

        # ----------------------------------------------------------------
        # 4. Small, Tasteful Clean-Energy Branding Card
        # ----------------------------------------------------------------
        st.markdown(
            f"""
<div class="stitch-promo-card">
    <div class="stitch-promo-icon">☀️</div>
    <div>
        <div class="stitch-promo-title">Empowering Greener India</div>
        <div class="stitch-promo-desc">Reliable information for a brighter, cleaner future.</div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------------------
        # 5. Restrained Version / Technology Footer
        # ----------------------------------------------------------------
        st.markdown(
            f"""
<div class="stitch-version-stamp">
    <span style="color:#20C997;font-size:13px;">🌱</span>
    <span><b>SolarSense v1.0</b> &bull; LangChain &bull; Gemini &bull; FAISS</span>
</div>
""",
            unsafe_allow_html=True,
        )
