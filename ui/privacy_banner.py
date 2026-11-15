"""
SolarSense AI — Privacy Banner Component
Fixed bottom privacy banner bar inspired by clean-energy web applications.
Truthful to actual application usage: local session state, zero third-party tracking.
"""

import streamlit as st


def render_privacy_banner(T: dict):
    """
    Renders a tasteful, fixed bottom privacy banner if user hasn't made a choice.
    Allows customizing preferences or dismissing with clear persistence.
    """
    if "privacy_consent" not in st.session_state:
        st.session_state["privacy_consent"] = None

    if "privacy_show_customizer" not in st.session_state:
        st.session_state["privacy_show_customizer"] = False

    # If consent has been given and customizer is not open, don't show the sticky bar
    if st.session_state["privacy_consent"] is not None and not st.session_state["privacy_show_customizer"]:
        return

    # Scoped CSS for bottom privacy banner
    st.html(
        """
        <style>
        .privacy-banner-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 99999;
            background: #FFFFFF;
            border-top: 1.5px solid #C9DCCF;
            box-shadow: 0 -4px 20px rgba(8, 127, 91, 0.08);
            padding: 16px 28px;
            animation: slideUp 0.25s ease-out;
        }
        @keyframes slideUp {
            from { transform: translateY(100%); }
            to { transform: translateY(0); }
        }
        .privacy-banner-title {
            font-size: 0.96rem;
            font-weight: 800;
            color: #052E24;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .privacy-banner-text {
            font-size: 0.82rem;
            color: #64756B;
            line-height: 1.5;
            max-width: 920px;
        }
        /* Extra padding at bottom of page so banner never obscures content */
        .main .block-container {
            padding-bottom: 120px !important;
        }
        </style>
        """
    )

    # 1. Customization modal/panel if requested
    if st.session_state["privacy_show_customizer"]:
        with st.container():
            st.html(
                """
                <div style="background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:16px; padding:24px 28px; margin:20px 0; box-shadow:0 8px 24px rgba(8,127,91,0.10);">
                    <div style="font-size:1.15rem; font-weight:800; color:#052E24; margin-bottom:8px;">Privacy & Storage Preferences</div>
                    <p style="font-size:0.85rem; color:#64756B; margin-bottom:16px;">
                        SolarSense is designed with privacy-first principles. We never run third-party tracking, advertising pixels, or cross-site fingerprinting.
                    </p>
                </div>
                """
            )
            col_pref1, col_pref2 = st.columns(2)
            with col_pref1:
                st.checkbox("Strictly Necessary Session State (Chat history, active questions, authentication)", value=True, disabled=True, key="pref_essential")
                st.caption("Required for the conversational RAG assistant to process prompts and maintain state.")
            with col_pref2:
                pref_opt = st.checkbox("Functional UI Preferences (Theme, sidebar layout, calculator defaults)", value=True, key="pref_functional")
                st.caption("Allows persisting light/dark mode and calculator inputs locally.")

            save_col1, save_col2, _ = st.columns([2.5, 2.5, 7])
            with save_col1:
                if st.button("Save Preferences", key="save_privacy_prefs", type="primary", use_container_width=True):
                    st.session_state["privacy_consent"] = "custom"
                    st.session_state["privacy_show_customizer"] = False
                    st.rerun()
            with save_col2:
                if st.button("Cancel", key="cancel_privacy_prefs", use_container_width=True):
                    st.session_state["privacy_show_customizer"] = False
                    st.rerun()
            return

    # 2. Main sticky banner
    st.html(
        """
        <div class="privacy-banner-container">
            <div style="max-width:1240px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:24px; flex-wrap:wrap;">
                <div style="flex:1; min-width:320px;">
                    <div class="privacy-banner-title">
                        <span>🛡️</span> Your privacy matters
                    </div>
                    <div class="privacy-banner-text">
                        SolarSense uses local session storage solely to maintain your active solar questions, document citations, and UI configuration.
                        We do not use advertising, marketing, or third-party profiling trackers.
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # Place interactive Streamlit buttons in a compact row right below/within banner bounds
    _, btn_c1, btn_c2, btn_c3 = st.columns([5.5, 2.1, 2.2, 2.2])

    with btn_c1:
        if st.button("Customize", key="privacy_btn_customize", use_container_width=True):
            st.session_state["privacy_show_customizer"] = True
            st.rerun()

    with btn_c2:
        if st.button("Reject Optional", key="privacy_btn_reject", use_container_width=True):
            st.session_state["privacy_consent"] = "essential_only"
            st.session_state["privacy_show_customizer"] = False
            st.rerun()

    with btn_c3:
        if st.button("Accept All", key="privacy_btn_accept", type="primary", use_container_width=True):
            st.session_state["privacy_consent"] = "all"
            st.session_state["privacy_show_customizer"] = False
            st.rerun()
