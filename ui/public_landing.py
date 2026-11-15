"""
SolarSense AI — Public Landing Page
High-fidelity implementation of the approved SolarSense Public SaaS Landing Page.
Features:
- Actual SolarSense logo asset
- Sticky navigation header with smooth section scrolling
- Photographic sunset hero with midnight-blue scrim gradient
- Split-image "Your Solar Questions, Answered with Context" section
- 3-step "How It Works" onboarding progression
- 6-card "Knowledge Engine" feature grid with green interaction states
- Browser-frame interactive product preview
- Centered final CTA section with paired action buttons
- 4-column structured footer
- Non-intrusive bottom privacy banner
"""

import base64
import os
import textwrap
import streamlit as st

from ui.privacy_banner import render_privacy_banner


def _get_image_b64(rel_path: str) -> str:
    """Read a local asset file and return its base64 string."""
    if os.path.exists(rel_path):
        try:
            with open(rel_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""


def _render_html(html_str: str):
    """Safely render application-authored HTML using st.html with dedent."""
    clean = textwrap.dedent(html_str).strip()
    st.html(clean)


def render_public_landing(T: dict):
    """Renders the complete public-facing landing page."""

    # 1. Scoped CSS for public landing: sticky header, grey-green canvas, smooth scrolling
    _render_html(
        """
        <style>
        section[data-testid="stSidebar"] { display: none !important; }
        button[data-testid="stExpandSidebarButton"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        
        .stApp,
        div[data-testid="stAppViewContainer"],
        section.main {
            background-color: #D3E2D6 !important;
            background: #D3E2D6 !important;
        }

        .main .block-container {
            max-width: 1280px !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-bottom: 4rem !important;
        }

        /* Smooth anchor scrolling with offset for sticky header */
        html {
            scroll-behavior: smooth;
        }
        #home, #about, #how-it-works, #features, #knowledge, #preview {
            scroll-margin-top: 112px;
        }

        /* Sticky Navigation Bar Container */
        .public-sticky-nav {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999999;
            background: rgba(211, 226, 214, 0.98);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border-bottom: 1.5px solid #C9DCCF;
            padding: 16px 2.5rem;
            box-shadow: 0 4px 22px rgba(8, 127, 91, 0.08);
        }

        /* Push page content below fixed navbar (~70px tall) with generous breathing room */
        .main .block-container,
        div[data-testid="stMainBlockContainer"] {
            max-width: 1280px !important;
            padding-top: 104px !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-bottom: 4rem !important;
        }

        /* Hero main heading typography */
        .hero-main-heading {
            font-size: 3.1rem !important;
            font-weight: 800 !important;
            line-height: 1.24 !important;
            letter-spacing: -0.025em !important;
            margin: 0 0 20px 0 !important;
            color: #FFFFFF !important;
        }

        /* Solar installation photograph card: height balanced with the complete 3-card left section */
        .solar-photo-card {
            position: relative;
            border-radius: 20px;
            overflow: hidden;
            border: 1.5px solid #C9DCCF;
            box-shadow: 0 10px 28px -4px rgba(8, 127, 91, 0.12);
            width: 100%;
            height: 524px;
            display: flex;
        }

        @media (max-width: 900px) {
            .nav-links-center { display: none !important; }
            .public-sticky-nav { padding: 12px 1.25rem !important; }
            .hero-main-heading { font-size: 2.3rem !important; line-height: 1.22 !important; }
            .solar-photo-card { height: 380px !important; margin-top: 18px !important; }
            .step-card { min-height: 220px !important; }
            .solar-feature-card { min-height: 215px !important; }
        }
        @media (max-width: 600px) {
            .main .block-container,
            div[data-testid="stMainBlockContainer"] {
                padding-top: 96px !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            .hero-main-heading { font-size: 1.85rem !important; line-height: 1.25 !important; }
            .hero-box { padding: 36px 22px !important; }
            .solar-photo-card { height: 290px !important; }
            .step-card { min-height: auto !important; height: auto !important; margin-bottom: 14px !important; }
            .solar-feature-card { min-height: auto !important; height: auto !important; margin-bottom: 14px !important; }
        }

        /* Inline nav demo button */
        .nav-btn-demo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 9px 22px;
            border: 1.5px solid #087F5B;
            border-radius: 10px;
            font-size: 0.88rem;
            font-weight: 700;
            color: #FFFFFF !important;
            text-decoration: none !important;
            background: #087F5B;
            transition: all 0.2s ease;
            white-space: nowrap;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(8, 127, 91, 0.25);
        }
        .nav-btn-demo:hover {
            background: #20C997;
            border-color: #20C997;
            color: #FFFFFF !important;
            box-shadow: 0 4px 16px rgba(32, 201, 151, 0.35);
            transform: translateY(-1px);
        }

        /* Mobile responsive navbar */
        @media (max-width: 900px) {
            .nav-links-center { display: none !important; }
            .public-sticky-nav { padding: 12px 1.25rem !important; }
        }

        /* Center nav link styling with hover states */
        .public-nav-link {
            color: #64756B;
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 0.88rem;
            font-weight: 600;
            transition: all 0.18s ease;
        }
        .public-nav-link:hover {
            color: #087F5B !important;
            background: rgba(32, 201, 151, 0.10);
        }
        .public-nav-link:active {
            color: #052E24 !important;
            background: rgba(32, 201, 151, 0.18);
        }

        /* Ensure stHtml elements inside column blocks stretch to 100% height for equal cards */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHtml"] {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
            height: 100% !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHtml"] > div {
            height: 100% !important;
        }

        /* Step Card Styling with Equal Height & Bottom Aligned Progress */
        .step-card {
            background: #FFFFFF;
            border: 1.5px solid #C9DCCF;
            border-radius: 18px;
            padding: 28px 24px;
            box-shadow: 0 2px 10px -2px rgba(8, 127, 91, 0.06);
            height: 100%;
            min-height: 242px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .step-card:hover {
            border-color: #20C997 !important;
            box-shadow: 0 8px 24px -4px rgba(32, 201, 151, 0.18) !important;
            transform: translateY(-2px);
        }

        /* Solar Feature Card Styling with Equal Height & Bottom Aligned Action Link */
        .solar-feature-card {
            background: #FFFFFF;
            border: 1.5px solid #C9DCCF;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 2px 8px -2px rgba(8, 127, 91, 0.06);
            height: 100%;
            min-height: 236px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .solar-feature-card:hover {
            border-color: #20C997 !important;
            background: #FFFFFF !important;
            box-shadow: 0 8px 24px -4px rgba(32, 201, 151, 0.18) !important;
            transform: translateY(-2px);
        }

        /* Button Styling */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button[kind="primary"] {
            background-color: #087F5B !important;
            border-color: #087F5B !important;
            color: #FFFFFF !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #052E24 !important;
            border-color: #052E24 !important;
            box-shadow: 0 4px 14px rgba(5, 46, 36, 0.35) !important;
        }
        .stButton > button:focus {
            outline: 2px solid #20C997 !important;
            outline-offset: 2px !important;
        }
        </style>
        """
    )

    logo_b64 = _get_image_b64("logo.jpg")
    hero_sunset_b64 = _get_image_b64("assets/landing_hero_sunset.png")
    home_solar_b64 = _get_image_b64("assets/landing_home_solar.png")

    if logo_b64:
        brand_logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" alt="SolarSense Logo" style="width:36px;height:36px;border-radius:10px;object-fit:cover;box-shadow:0 2px 6px rgba(8,127,91,0.25);"/>'
    else:
        brand_logo_html = '<div style="width:36px;height:36px;border-radius:10px;background:#087F5B;color:#A3E635;display:flex;align-items:center;justify-content:center;font-size:1.25rem;font-weight:800;box-shadow:0 2px 6px rgba(8,127,91,0.25);">☀️</div>'

    # -------------------------------------------------------------------------
    # 1. STICKY PUBLIC TOP NAVIGATION BAR (fully self-contained HTML)
    # -------------------------------------------------------------------------
    _render_html("<div id='home'></div>")

    _render_html(
        f"""
        <div class="public-sticky-nav" id="solarsense-topnav">
            <div style="max-width:1240px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:16px;">
                <!-- Left: Brand Logo & Name -->
                <div style="display:flex; align-items:center; gap:12px; min-width:200px; flex-shrink:0;">
                    {brand_logo_html}
                    <div>
                        <div style="font-size:1.15rem; font-weight:800; color:#052E24; letter-spacing:-0.02em; line-height:1.1;">SolarSense AI</div>
                        <div style="font-size:0.7rem; font-weight:600; color:#64756B; letter-spacing:0.02em;">Clean Energy Intelligence</div>
                    </div>
                </div>

                <!-- Center: Navigation Links -->
                <div class="nav-links-center" style="display:flex; align-items:center; gap:4px; flex-wrap:wrap; justify-content:center; flex:1;">
                    <a href="#home" class="public-nav-link">Home</a>
                    <a href="#features" class="public-nav-link">Features</a>
                    <a href="#how-it-works" class="public-nav-link">How It Works</a>
                    <a href="#knowledge" class="public-nav-link">Solar Knowledge</a>
                    <a href="#about" class="public-nav-link">About</a>
                </div>

                <!-- Right: Demo Button (direct dashboard access) -->
                <div style="display:flex; align-items:center; gap:12px; flex-shrink:0;">
                    <a href="?page=dashboard" target="_self" class="nav-btn-demo">Try Demo →</a>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 2. HERO SECTION (Approved Sunset Solar Panels Visual with Scrim Overlay)
    # -------------------------------------------------------------------------
    hero_bg_style = ""
    if hero_sunset_b64:
        hero_bg_style = f"background-image: linear-gradient(to right, rgba(3, 31, 24, 0.96) 0%, rgba(5, 46, 36, 0.90) 50%, rgba(5, 46, 36, 0.40) 100%), url('data:image/png;base64,{hero_sunset_b64}'); background-size: cover; background-position: center right;"
    else:
        hero_bg_style = "background: linear-gradient(135deg, #052E24 0%, #087F5B 100%);"

    _render_html(
        f"""
        <div class="hero-box" style="{hero_bg_style} border-radius:24px; padding:56px 48px; color:#FFFFFF; margin-top:16px; margin-bottom:24px; box-shadow:0 14px 38px -8px rgba(5,46,36,0.38); position:relative; overflow:hidden;">
            <div style="max-width:720px; position:relative; z-index:2;">
                <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:9999px; background:rgba(32,201,151,0.20); border:1px solid rgba(163,230,53,0.45); font-size:0.75rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#A3E635; margin-bottom:18px;">
                    <span>⚡</span> AI-POWERED SOLAR INTELLIGENCE
                </div>
                <h1 class="hero-main-heading">
                    <span style="display:block; color:#FFFFFF; margin-bottom:6px; text-shadow:0 2px 14px rgba(3,31,24,0.75);">Make Smarter Solar</span>
                    <span style="display:block; color:#20C997; text-shadow:0 2px 14px rgba(3,31,24,0.75);">Decisions with AI.</span>
                </h1>
                <p style="font-size:1.06rem; line-height:1.65; color:#E2ECE7; margin-bottom:28px; font-weight:400; max-width:640px;">
                    Explore rooftop solar, understand PM Surya Ghar guidance, learn about battery storage, and ask questions using a knowledge assistant grounded in available reference documents.
                </p>
                <div style="display:flex; flex-wrap:wrap; gap:16px; margin-bottom:16px;">
                    <span style="display:inline-flex; align-items:center; gap:6px; font-size:0.84rem; font-weight:600; color:#D1FAE5;">
                        <span style="color:#20C997;font-weight:800;">✓</span> Source-Backed Answers
                    </span>
                    <span style="display:inline-flex; align-items:center; gap:6px; font-size:0.84rem; font-weight:600; color:#D1FAE5; margin-left:12px;">
                        <span style="color:#20C997;font-weight:800;">✓</span> Solar Knowledge Assistance
                    </span>
                    <span style="display:inline-flex; align-items:center; gap:6px; font-size:0.84rem; font-weight:600; color:#D1FAE5; margin-left:12px;">
                        <span style="color:#20C997;font-weight:800;">✓</span> Document-Grounded Intelligence
                    </span>
                </div>
            </div>
        </div>
        """
    )

    # Hero Action Buttons
    hero_btn_col1, hero_btn_col2, _ = st.columns([2.6, 3.2, 6.2], gap="medium")
    with hero_btn_col1:
        if st.button("Try Demo →", key="hero_primary_cta", type="primary", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["preview_mode"] = True
            st.session_state["user_name"] = "Demo Visitor"
            st.session_state["current_page"] = "Chat Assistant"
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.rerun()
    with hero_btn_col2:
        if st.button("Discover How It Works ▾", key="hero_howitworks_cta", use_container_width=True):
            _render_html("<script>window.location.hash = '#how-it-works';</script>")

    _render_html("<div style='height:44px;' id='about'></div>")

    # -------------------------------------------------------------------------
    # 3. WHAT IS SOLARSENSE (Your Solar Questions, Answered with Context)
    # -------------------------------------------------------------------------
    exp_col1, exp_col2 = st.columns([58, 42], gap="large")

    with exp_col1:
        _render_html(
            """
            <div style="height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:inline-flex; align-items:center; gap:6px; font-size:0.74rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:#087F5B; margin-bottom:10px;">
                        <span>🌱</span> DOCUMENT-GROUNDED INTELLIGENCE
                    </div>
                    <h2 style="font-size:2.2rem; font-weight:800; line-height:1.2; letter-spacing:-0.02em; color:#052E24; margin:0 0 14px 0;">
                        Your Solar Questions,<br/><span style="color:#087F5B;">Answered with Context.</span>
                    </h2>
                    <p style="font-size:0.95rem; line-height:1.65; color:#64756B; margin-bottom:20px;">
                        SolarSense brings together reliable information into one convenient place. Ask questions in natural language about rooftop solar, explore state subsidies, learn about battery storage, and examine supporting document references when provided.
                    </p>
                </div>
                <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:0;">
                    <div style="display:flex; align-items:flex-start; gap:14px; background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:14px; padding:16px 18px; box-shadow:0 1px 4px rgba(5,46,36,0.05);">
                        <div style="width:38px; height:38px; border-radius:10px; background:#E9F2EA; color:#087F5B; display:flex; align-items:center; justify-content:center; font-size:1.2rem; flex-shrink:0;">
                            📄
                        </div>
                        <div>
                            <div style="font-size:0.92rem; font-weight:700; color:#052E24;">Find Relevant Information</div>
                            <div style="font-size:0.8rem; color:#64756B; line-height:1.45; margin-top:2px;">Inquire freely about subsidies, equipment, and tariffs instead of searching through scattered government PDFs manually.</div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:flex-start; gap:14px; background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:14px; padding:16px 18px; box-shadow:0 1px 4px rgba(5,46,36,0.05);">
                        <div style="width:38px; height:38px; border-radius:10px; background:#EFF6FF; color:#2563EB; display:flex; align-items:center; justify-content:center; font-size:1.2rem; flex-shrink:0;">
                            🔍
                        </div>
                        <div>
                            <div style="font-size:0.92rem; font-weight:700; color:#052E24;">Understand the Response</div>
                            <div style="font-size:0.8rem; color:#64756B; line-height:1.45; margin-top:2px;">Read clear responses synthesized from reference solar policy documents, technical manuals, and official DISCOM circulars.</div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:flex-start; gap:14px; background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:14px; padding:16px 18px; box-shadow:0 1px 4px rgba(5,46,36,0.05);">
                        <div style="width:38px; height:38px; border-radius:10px; background:#FEF3C7; color:#D97706; display:flex; align-items:center; justify-content:center; font-size:1.2rem; flex-shrink:0;">
                            💡
                        </div>
                        <div>
                            <div style="font-size:0.92rem; font-weight:700; color:#052E24;">Check Supporting Sources</div>
                            <div style="font-size:0.8rem; color:#64756B; line-height:1.45; margin-top:2px;">Review verified source citations and official clauses alongside every response for complete transparency.</div>
                        </div>
                    </div>
                </div>
            </div>
            """
        )

    with exp_col2:
        img_html = ""
        if home_solar_b64:
            img_html = f'<img src="data:image/png;base64,{home_solar_b64}" alt="Rooftop Solar Villa Installation" style="width:100%; height:100%; object-fit:cover; border-radius:20px; display:block;"/>'
        else:
            img_html = '<div style="width:100%; height:524px; background:#E9F2EA; border-radius:20px; display:flex; align-items:center; justify-content:center; font-size:3rem;">🏡☀️</div>'

        _render_html(
            f"""
            <div style="display:flex; flex-direction:column; justify-content:flex-start; height:100%;">
                <div class="solar-photo-card">
                    {img_html}
                    <div style="position:absolute; bottom:16px; left:16px; right:16px; background:rgba(255,255,255,0.96); backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px); border:1.5px solid #C9DCCF; border-radius:12px; padding:12px 16px; display:flex; align-items:center; justify-content:space-between; box-shadow:0 4px 16px rgba(0,0,0,0.10);">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="width:10px; height:10px; border-radius:50%; background:#20C997; display:inline-block;"></span>
                            <div>
                                <div style="font-size:0.76rem; font-weight:800; color:#087F5B; text-transform:uppercase; letter-spacing:0.04em;">Residential PV Installation</div>
                                <div style="font-size:0.72rem; color:#64756B;">High-Efficiency Mono-PERC Array, 5 kW Grid-Tied</div>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:0.68rem; color:#64756B; display:block;">Irradiance</span>
                            <span style="font-size:0.82rem; font-weight:800; color:#087F5B;">5.4 kWh/m²</span>
                        </div>
                    </div>
                </div>
            </div>
            """
        )

    _render_html("<div style='height:50px;' id='how-it-works'></div>")

    # -------------------------------------------------------------------------
    # 4. HOW IT WORKS (Getting Started Is Simple - Three Steps)
    # -------------------------------------------------------------------------
    _render_html(
        """
        <div style="text-align:center; max-width:700px; margin:0 auto 36px auto;">
            <div style="display:inline-flex; align-items:center; gap:6px; font-size:0.74rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:#087F5B; margin-bottom:8px;">
                <span>📋</span> SEAMLESS ONBOARDING
            </div>
            <h2 style="font-size:2.2rem; font-weight:800; letter-spacing:-0.02em; color:#052E24; margin:0 0 10px 0;">
                Getting Started Is Simple
            </h2>
            <p style="font-size:0.95rem; color:#64756B; line-height:1.55; margin:0;">
                Three straightforward steps to unlock source-backed clarity for your rooftop solar decisions.
            </p>
        </div>
        """
    )

    step_col1, step_col2, step_col3 = st.columns(3, gap="medium")

    with step_col1:
        _render_html(
            """
            <div class="step-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px;">
                        <div style="width:40px; height:40px; border-radius:50%; background:#087F5B; color:#FFFFFF; font-weight:800; font-size:1.15rem; display:flex; align-items:center; justify-content:center;">
                            1
                        </div>
                        <span style="font-size:1.3rem;">👤</span>
                    </div>
                    <div style="font-size:1.15rem; font-weight:800; color:#052E24; margin-bottom:8px; line-height:1.3;">Launch Interactive Demo</div>
                    <div style="font-size:0.84rem; color:#64756B; line-height:1.55; flex-grow:1;">Click Try Demo to directly access the SolarSense dashboard and explore verified solar intelligence.</div>
                </div>
                <div style="margin-top:24px; width:100%; height:4px; background:#E9F2EA; border-radius:9999px; overflow:hidden;">
                    <div style="width:33%; height:100%; background:#087F5B;"></div>
                </div>
            </div>
            """
        )

    with step_col2:
        _render_html(
            """
            <div class="step-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px;">
                        <div style="width:40px; height:40px; border-radius:50%; background:#052E24; color:#FFFFFF; font-weight:800; font-size:1.15rem; display:flex; align-items:center; justify-content:center;">
                            2
                        </div>
                        <span style="font-size:1.3rem;">💬</span>
                    </div>
                    <div style="font-size:1.15rem; font-weight:800; color:#052E24; margin-bottom:8px; line-height:1.3;">Ask a Solar Question</div>
                    <div style="font-size:0.84rem; color:#64756B; line-height:1.55; flex-grow:1;">Ask about PM Surya Ghar, state subsidies, net metering policies, or choose from curated quick topics.</div>
                </div>
                <div style="margin-top:24px; width:100%; height:4px; background:#E9F2EA; border-radius:9999px; overflow:hidden;">
                    <div style="width:66%; height:100%; background:#052E24;"></div>
                </div>
            </div>
            """
        )

    with step_col3:
        _render_html(
            """
            <div class="step-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px;">
                        <div style="width:40px; height:40px; border-radius:50%; background:#20C997; color:#FFFFFF; font-weight:800; font-size:1.15rem; display:flex; align-items:center; justify-content:center;">
                            3
                        </div>
                        <span style="font-size:1.3rem;">✅</span>
                    </div>
                    <div style="font-size:1.15rem; font-weight:800; color:#052E24; margin-bottom:8px; line-height:1.3;">Explore Answers & Sources</div>
                    <div style="font-size:0.84rem; color:#64756B; line-height:1.55; flex-grow:1;">Read clear responses, inspect supporting document references when available, and ask follow-up questions.</div>
                </div>
                <div style="margin-top:24px; width:100%; height:4px; background:#E9F2EA; border-radius:9999px; overflow:hidden;">
                    <div style="width:100%; height:100%; background:#20C997;"></div>
                </div>
            </div>
            """
        )

    _render_html("<div style='height:50px;' id='features'></div><div id='knowledge'></div>")

    # -------------------------------------------------------------------------
    # 5. FEATURES SECTION (Everything You Need to Explore Solar - 6 Cards)
    # -------------------------------------------------------------------------
    _render_html(
        """
        <div style="display:flex; align-items:flex-end; justify-content:space-between; margin-bottom:32px; flex-wrap:wrap; gap:16px;">
            <div style="max-width:650px;">
                <div style="display:inline-flex; align-items:center; gap:6px; font-size:0.74rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:#087F5B; margin-bottom:8px;">
                    <span>⚡</span> KNOWLEDGE ENGINE
                </div>
                <h2 style="font-size:2.2rem; font-weight:800; letter-spacing:-0.02em; color:#052E24; margin:0 0 8px 0;">
                    Everything You Need to Explore Solar
                </h2>
                <p style="font-size:0.95rem; color:#64756B; line-height:1.55; margin:0;">
                    A comprehensive suite of intelligence tools designed to remove guesswork from your solar journey.
                </p>
            </div>
            <div style="display:inline-flex; align-items:center; gap:6px; padding:6px 14px; border-radius:9999px; background:#E9F2EA; color:#087F5B; font-size:0.78rem; font-weight:700;">
                <span>⚡</span> 6 Key Focus Areas
            </div>
        </div>
        """
    )

    feat_row1_col1, feat_row1_col2, feat_row1_col3 = st.columns(3, gap="medium")

    with feat_row1_col1:
        _render_html(
            """
            <div class="solar-feature-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="width:38px; height:38px; border-radius:10px; background:#E9F2EA; color:#087F5B; display:flex; align-items:center; justify-content:center; font-size:1.2rem; margin-bottom:14px;">
                        🏛️
                    </div>
                    <div style="font-size:1.05rem; font-weight:800; color:#052E24; margin-bottom:6px; line-height:1.3;">Solar Scheme Guidance</div>
                    <div style="font-size:0.82rem; color:#64756B; line-height:1.5; flex-grow:1;">Understand official provisions under PM Surya Ghar and state rooftop solar scheme documentation.</div>
                </div>
                <div style="margin-top:16px; font-size:0.78rem; font-weight:700; color:#087F5B; padding-top:4px;">Explore Scheme Details →</div>
            </div>
            """
        )

    with feat_row1_col2:
        _render_html(
            """
            <div class="solar-feature-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="width:38px; height:38px; border-radius:10px; background:#E9F2EA; color:#087F5B; display:flex; align-items:center; justify-content:center; font-size:1.2rem; margin-bottom:14px;">
                        💰
                    </div>
                    <div style="font-size:1.05rem; font-weight:800; color:#052E24; margin-bottom:6px; line-height:1.3;">Subsidy Information</div>
                    <div style="font-size:0.82rem; color:#64756B; line-height:1.5; flex-grow:1;">Explore central (MNRE) DBT subsidy slabs, ₹30,000/kW up to 2 kW, and ₹78,000 maximum cap calculations.</div>
                </div>
                <div style="margin-top:16px; font-size:0.78rem; font-weight:700; color:#087F5B; padding-top:4px;">Calculate Potential Grants →</div>
            </div>
            """
        )

    with feat_row1_col3:
        _render_html(
            """
            <div class="solar-feature-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="width:38px; height:38px; border-radius:10px; background:#FEF3C7; color:#92400E; display:flex; align-items:center; justify-content:center; font-size:1.2rem; margin-bottom:14px;">
                        🧮
                    </div>
                    <div style="font-size:1.05rem; font-weight:800; color:#052E24; margin-bottom:6px; line-height:1.3;">Solar Savings & Calculator</div>
                    <div style="font-size:0.82rem; color:#64756B; line-height:1.5; flex-grow:1;">Accurate sizing formulas estimating system kW capacity, roof area requirements, bill savings, and payback period.</div>
                </div>
                <div style="margin-top:16px; font-size:0.78rem; font-weight:700; color:#087F5B; padding-top:4px;">View Financial Simulator →</div>
            </div>
            """
        )

    _render_html("<div style='height:16px;'></div>")

    feat_row2_col1, feat_row2_col2, feat_row2_col3 = st.columns(3, gap="medium")

    with feat_row2_col1:
        _render_html(
            """
            <div class="solar-feature-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="width:38px; height:38px; border-radius:10px; background:#EFF6FF; color:#1D4ED8; display:flex; align-items:center; justify-content:center; font-size:1.2rem; margin-bottom:14px;">
                        🔋
                    </div>
                    <div style="font-size:1.05rem; font-weight:800; color:#052E24; margin-bottom:6px; line-height:1.3;">Battery Storage Knowledge</div>
                    <div style="font-size:0.82rem; color:#64756B; line-height:1.5; flex-grow:1;">Learn about Lithium vs Lead-acid chemistry, critical backup loads, depth of discharge, and hybrid inverter logic.</div>
                </div>
                <div style="margin-top:16px; font-size:0.78rem; font-weight:700; color:#087F5B; padding-top:4px;">Review Storage Basics →</div>
            </div>
            """
        )

    with feat_row2_col2:
        _render_html(
            """
            <div class="solar-feature-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="width:38px; height:38px; border-radius:10px; background:#F3E8FF; color:#7E22CE; display:flex; align-items:center; justify-content:center; font-size:1.2rem; margin-bottom:14px;">
                        🔄
                    </div>
                    <div style="font-size:1.05rem; font-weight:800; color:#052E24; margin-bottom:6px; line-height:1.3;">Policy & Net Metering</div>
                    <div style="font-size:0.82rem; color:#64756B; line-height:1.5; flex-grow:1;">Explore state DISCOM interconnection rules, bi-directional meter sanctioning, feed-in tariffs, and settlement cycles.</div>
                </div>
                <div style="margin-top:16px; font-size:0.78rem; font-weight:700; color:#087F5B; padding-top:4px;">Explore Regional Policies →</div>
            </div>
            """
        )

    with feat_row2_col3:
        _render_html(
            """
            <div class="solar-feature-card">
                <div style="flex:1 1 auto; display:flex; flex-direction:column;">
                    <div style="width:38px; height:38px; border-radius:10px; background:#FFE4E6; color:#BE123C; display:flex; align-items:center; justify-content:center; font-size:1.2rem; margin-bottom:14px;">
                        📚
                    </div>
                    <div style="font-size:1.05rem; font-weight:800; color:#052E24; margin-bottom:6px; line-height:1.3;">AI Document Search</div>
                    <div style="font-size:0.82rem; color:#64756B; line-height:1.5; flex-grow:1;">Ask questions and review verbatim source citations, PDF excerpts, and verified policy clauses instantly.</div>
                </div>
                <div style="margin-top:16px; font-size:0.78rem; font-weight:700; color:#087F5B; padding-top:4px;">Try Natural Language Search →</div>
            </div>
            """
        )

    _render_html("<div style='height:50px;' id='preview'></div>")

    # -------------------------------------------------------------------------
    # 6. PRODUCT SHOWCASE (PREVIEW OF THE AI EXPERIENCE - RENDERED AS DOM)
    # -------------------------------------------------------------------------
    _render_html(
        """
        <div style="text-align:center; max-width:700px; margin:0 auto 32px auto;">
            <div style="display:inline-flex; align-items:center; gap:6px; font-size:0.74rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:#087F5B; margin-bottom:8px;">
                <span>🖥️</span> INTERACTIVE PRODUCT PREVIEW
            </div>
            <h2 style="font-size:2.2rem; font-weight:800; letter-spacing:-0.02em; color:#052E24; margin:0 0 10px 0;">
                Experience the AI Assistant in Action
            </h2>
            <p style="font-size:0.95rem; color:#64756B; line-height:1.55; margin:0;">
                A live demonstration of the conversational interface designed for verified rooftop solar decisions.
            </p>
        </div>

        <div style="background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:20px; box-shadow:0 12px 36px -8px rgba(8,127,91,0.12); overflow:hidden; margin-bottom:44px;">
            <div style="background:#E9F2EA; border-bottom:1.5px solid #C9DCCF; padding:12px 18px; display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="width:11px; height:11px; border-radius:50%; background:#EF4444; display:inline-block;"></span>
                    <span style="width:11px; height:11px; border-radius:50%; background:#F59E0B; display:inline-block;"></span>
                    <span style="width:11px; height:11px; border-radius:50%; background:#20C997; display:inline-block;"></span>
                </div>
                <div style="background:#FFFFFF; border:1px solid #C9DCCF; border-radius:8px; padding:4px 20px; font-size:0.75rem; font-weight:600; color:#64756B; font-family:monospace;">
                    app.solarsense.ai/assistant
                </div>
                <div style="font-size:0.75rem; font-weight:700; color:#087F5B; display:flex; align-items:center; gap:6px;">
                    <span style="width:8px; height:8px; border-radius:50%; background:#20C997;"></span> 61 Docs Live
                </div>
            </div>

            <div style="padding:28px 32px; background:#D3E2D6;">
                <div style="display:grid; grid-template-columns:7fr 3fr; gap:24px;">
                    <div>
                        <div style="display:flex; justify-content:flex-end; margin-bottom:16px;">
                            <div style="background:#087F5B; color:#FFFFFF; border-radius:14px 14px 2px 14px; padding:12px 18px; max-width:85%; font-size:0.88rem; font-weight:500; line-height:1.45; box-shadow:0 2px 8px rgba(8,127,91,0.2);">
                                What is the maximum central subsidy under PM Surya Ghar for a 3kW system?
                            </div>
                        </div>

                        <div style="background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:14px 14px 14px 2px; padding:18px 22px; font-size:0.86rem; color:#052E24; line-height:1.6; box-shadow:0 2px 8px -2px rgba(8,127,91,0.06);">
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; border-bottom:1px solid #C9DCCF; padding-bottom:8px;">
                                <div style="display:flex; align-items:center; gap:8px;">
                                    <span style="font-size:1.1rem;">☀️</span>
                                    <span style="font-weight:800; color:#087F5B; font-size:0.9rem;">SolarSense AI</span>
                                </div>
                                <span style="background:#E9F2EA; color:#087F5B; font-size:0.7rem; font-weight:700; padding:2px 8px; border-radius:5px; border:1px solid #C9DCCF;">
                                    ✅ Grounded (MNRE Policy)
                                </span>
                            </div>
                            <p style="margin:0 0 10px 0;">
                                Under the <strong>PM Surya Ghar: Muft Bijli Yojana</strong> guidelines, residential rooftop solar systems receive Central Financial Assistance (DBT Subsidy) calculated across specific capacity slabs:
                            </p>
                            <div style="background:#E9F2EA; border:1px solid #C9DCCF; border-radius:10px; padding:10px 14px; margin-bottom:12px; font-size:0.82rem;">
                                <div>• <strong>First 2 kW:</strong> ₹30,000 per kW = <strong>₹60,000</strong></div>
                                <div>• <strong>Additional 3rd kW:</strong> ₹18,000 per kW = <strong>₹18,000</strong></div>
                                <div style="margin-top:6px; padding-top:6px; border-top:1px dashed #C9DCCF; font-weight:800; color:#087F5B;">
                                    Total Subsidy for 3 kW = ₹78,000 (Maximum Cap)
                                </div>
                            </div>
                            <div style="display:flex; align-items:center; gap:6px; font-size:0.74rem; color:#64756B; border-top:1px solid #C9DCCF; padding-top:8px;">
                                <span style="color:#087F5B;">📄 Source:</span> <em>PM_Surya_Ghar_Operational_Guidelines_2024.pdf §4.2</em>
                            </div>
                        </div>

                        <div style="margin-top:16px; background:#FFFFFF; border:1px solid #C9DCCF; border-radius:12px; padding:8px 14px; display:flex; align-items:center; gap:10px;">
                            <span style="color:#64756B; font-size:1rem;">✨</span>
                            <span style="font-size:0.82rem; color:#64756B; flex:1;">Ask about net metering in Maharashtra, inverter warranties, or payback time...</span>
                            <span style="background:#087F5B; color:#FFFFFF; border-radius:8px; padding:6px 12px; font-size:0.75rem; font-weight:700;">Send ➔</span>
                        </div>
                    </div>

                    <div style="display:flex; flex-direction:column; gap:12px;">
                        <div style="background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:12px; padding:14px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px;">
                                <span style="font-size:0.74rem; font-weight:800; color:#087F5B; text-transform:uppercase;">Document Ingestion</span>
                                <span style="background:#E9F2EA; color:#087F5B; font-size:0.68rem; font-weight:700; padding:1px 6px; border-radius:4px;">Ready</span>
                            </div>
                            <div style="font-size:1.25rem; font-weight:800; color:#052E24;">61 Docs Live</div>
                            <div style="font-size:0.72rem; color:#64756B; margin-top:2px;">FAISS FlatL2 Vectorstore Online</div>
                        </div>

                        <div style="background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:12px; padding:14px; box-shadow:0 1px 4px rgba(0,0,0,0.04);">
                            <div style="font-size:0.74rem; font-weight:800; color:#087F5B; text-transform:uppercase; margin-bottom:6px;">Suggested Inquiries</div>
                            <div style="display:flex; flex-direction:column; gap:6px; font-size:0.76rem; color:#052E24;">
                                <div style="background:#E9F2EA; border:1px solid #C9DCCF; border-radius:6px; padding:6px 8px;">• How do I claim PM Surya Ghar subsidy?</div>
                                <div style="background:#E9F2EA; border:1px solid #C9DCCF; border-radius:6px; padding:6px 8px;">• What is the payback period for 5kW solar?</div>
                                <div style="background:#E9F2EA; border:1px solid #C9DCCF; border-radius:6px; padding:6px 8px;">• Do I need batteries if I have net metering?</div>
                            </div>
                        </div>

                        <div style="background:linear-gradient(135deg,#052E24 0%,#087F5B 100%); color:#FFFFFF; border-radius:12px; padding:12px 14px; display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.3rem;">🌱</span>
                            <div style="font-size:0.74rem; line-height:1.35;">
                                <strong style="color:#A3E635; display:block;">Zero Guesswork</strong>
                                Responses are synthesized strictly from empirical reference materials.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    # -------------------------------------------------------------------------
    # 7. FINAL CALL TO ACTION (Ready to Explore Solar with Confidence?)
    # -------------------------------------------------------------------------
    _render_html(
        """
        <div style="background:linear-gradient(135deg, #052E24 0%, #087F5B 100%); border:1px solid rgba(255, 255, 255, 0.15); border-radius:24px; padding:48px 36px; text-align:center; color:#FFFFFF; margin-bottom:28px; box-shadow:0 14px 34px -6px rgba(5,46,36,0.38);">
            <div style="display:inline-flex; align-items:center; gap:6px; padding:5px 14px; border-radius:9999px; background:rgba(32,201,151,0.22); border:1px solid rgba(163,230,53,0.4); font-size:0.72rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#A3E635; margin-bottom:16px;">
                <span>✨</span> DEMOCRATIZING CLEAN TECH KNOWLEDGE
            </div>
            <h2 style="font-size:2.4rem; font-weight:800; line-height:1.2; letter-spacing:-0.02em; color:#FFFFFF; margin:0 0 12px 0;">
                Ready to Explore Solar<br/>with Confidence?
            </h2>
            <p style="font-size:1rem; color:#E2ECE7; max-width:620px; margin:0 auto 24px auto; line-height:1.6;">
                Start exploring rooftop solar knowledge with an AI assistant designed to help you find and understand information from reference documents.
            </p>
        </div>
        """
    )

    # CTA Buttons underneath, centered horizontally
    _, cta_col, _ = st.columns([4.2, 3.6, 4.2], gap="medium")
    with cta_col:
        if st.button("Try Demo →", key="cta_bottom_demo", type="primary", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["preview_mode"] = True
            st.session_state["user_name"] = "Demo Visitor"
            st.session_state["current_page"] = "Chat Assistant"
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.rerun()

    _render_html("<div style='height:40px;'></div>")

    # -------------------------------------------------------------------------
    # 8. FOOTER (4-Column Layout with SolarSense Logo)
    # -------------------------------------------------------------------------
    _render_html(
        f"""
        <footer style="background:#E9F2EA; border-top:1.5px solid #C9DCCF; border-radius:18px; padding:40px 36px 24px 36px; margin-top:20px;">
            <div style="display:grid; grid-template-columns:4fr 2.5fr 2.5fr 3fr; gap:28px; margin-bottom:32px;">
                <div>
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                        {brand_logo_html}
                        <div>
                            <div style="font-size:1.15rem; font-weight:800; color:#052E24; line-height:1.1;">SolarSense AI</div>
                            <div style="font-size:0.7rem; font-weight:600; color:#64756B;">Clean Energy Intelligence</div>
                        </div>
                    </div>
                    <p style="font-size:0.82rem; color:#64756B; line-height:1.55; margin:0 0 12px 0;">
                        Your trusted clean-energy companion for rooftop solar decisions. Grounded answers, accurate subsidy guidance, and reliable reference documents.
                    </p>
                    <div style="font-size:0.75rem; font-weight:700; color:#087F5B;">Empirical Rigor • Environmental Optimism</div>
                </div>

                <div>
                    <div style="font-size:0.8rem; font-weight:800; color:#052E24; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:10px;">Platform</div>
                    <div style="display:flex; flex-direction:column; gap:6px; font-size:0.82rem; color:#64756B;">
                        <a href="#features" style="color:#64756B; text-decoration:none;">Features</a>
                        <a href="#how-it-works" style="color:#64756B; text-decoration:none;">How It Works</a>
                        <a href="#knowledge" style="color:#64756B; text-decoration:none;">Solar Knowledge</a>
                        <a href="#preview" style="color:#64756B; text-decoration:none;">AI Preview</a>
                    </div>
                </div>

                <div>
                    <div style="font-size:0.8rem; font-weight:800; color:#052E24; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:10px;">Company</div>
                    <div style="display:flex; flex-direction:column; gap:6px; font-size:0.82rem; color:#64756B;">
                        <a href="#about" style="color:#64756B; text-decoration:none;">About Us</a>
                        <span style="color:#64756B;">Research & Data</span>
                        <span style="color:#64756B;">Solar Policies</span>
                    </div>
                </div>

                <div>
                    <div style="font-size:0.8rem; font-weight:800; color:#052E24; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:10px;">Access</div>
                    <p style="font-size:0.82rem; color:#64756B; line-height:1.45; margin:0 0 10px 0;">
                        Ready to explore our tools and make an informed solar decision?
                    </p>
                    <div style="display:flex; gap:8px;">
                        <a href="?page=dashboard" target="_self" style="display:inline-block; padding:8px 18px; background:#087F5B; border-radius:8px; font-size:0.82rem; font-weight:700; color:#FFFFFF; text-decoration:none;">Try Demo →</a>
                    </div>
                </div>
            </div>

            <div style="display:flex; align-items:center; justify-content:space-between; border-top:1px solid #C9DCCF; padding-top:18px; font-size:0.76rem; color:#64756B; flex-wrap:wrap; gap:12px;">
                <div>© 2026 SolarSense AI Technologies Inc. All empirical models reserved.</div>
                <div style="display:flex; align-items:center; gap:18px;">
                    <span>Privacy Policy</span>
                    <span>Terms of Service</span>
                    <span>Methodology</span>
                </div>
            </div>
        </footer>
        """
    )

    # -------------------------------------------------------------------------
    # 9. BOTTOM PRIVACY BANNER
    # -------------------------------------------------------------------------
    render_privacy_banner(T)
