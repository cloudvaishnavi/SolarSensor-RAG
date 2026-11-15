from string import Template

THEMES = {
    "dark": {
        "bg_a": "#031F18",
        "bg_b": "#052E24",
        "bg_c": "#07382C",
        "sidebar_a": "#031F18",
        "sidebar_b": "#052E24",
        "surface": "#07382C",
        "surface_elevated": "#0B4436",
        "surface_alt": "#0E4D3E",
        "surface_subtle": "#125646",
        "border": "#166250",
        "border_soft": "#0E4D3E",
        "border_strong": "#20C997",
        "text": "#F4F8F2",
        "text_muted": "#A3C2B4",
        "text_dim": "#739B8B",
        "accent": "#20C997",
        "accent_strong": "#087F5B",
        "accent_soft": "rgba(32, 201, 151, 0.16)",
        "technical": "#20C997",
        "technical_soft": "rgba(32, 201, 151, 0.14)",
        "success": "#20C997",
        "success_soft": "rgba(32, 201, 151, 0.14)",
        "warning": "#FBBF24",
        "warning_soft": "rgba(251, 191, 36, 0.14)",
        "blue": "#38BDF8",
        "blue_soft": "rgba(56, 189, 248, 0.12)",
        "error": "#F87171",
        "error_soft": "rgba(248, 113, 113, 0.12)",
        "shadow_sm": "0 2px 10px -2px rgba(0, 0, 0, 0.25)",
        "shadow_md": "0 4px 16px -4px rgba(0, 0, 0, 0.35)",
        "shadow_lg": "0 8px 28px -6px rgba(0, 0, 0, 0.45)",
        "code_bg": "#031F18",
        "primary": "#087F5B",
        "secondary": "#20C997",
        "tertiary": "#A3E635",
        "glass_bg": "rgba(7, 56, 44, 0.88)",
        "theme_icon_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A3E635' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='4.5'/%3E%3Cline x1='12' y1='1.5' x2='12' y2='4'/%3E%3Cline x1='12' y1='20' x2='12' y2='22.5'/%3E%3Cline x1='4.58' y1='4.58' x2='6.35' y2='6.35'/%3E%3Cline x1='17.65' y1='17.65' x2='19.42' y2='19.42'/%3E%3Cline x1='1.5' y1='12' x2='4' y2='12'/%3E%3Cline x1='20' y1='12' x2='22.5' y2='12'/%3E%3Cline x1='4.58' y1='19.42' x2='6.35' y2='17.65'/%3E%3Cline x1='17.65' y1='6.35' x2='19.42' y2='4.58'/%3E%3C/svg%3E\")",
        "theme_icon_hover_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23A3E635' stroke='%23A3E635' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='4.5'/%3E%3Cline x1='12' y1='1.5' x2='12' y2='4'/%3E%3Cline x1='12' y1='20' x2='12' y2='22.5'/%3E%3Cline x1='4.58' y1='4.58' x2='6.35' y2='6.35'/%3E%3Cline x1='17.65' y1='17.65' x2='19.42' y2='19.42'/%3E%3Cline x1='1.5' y1='12' x2='4' y2='12'/%3E%3Cline x1='20' y1='12' x2='22.5' y2='12'/%3E%3Cline x1='4.58' y1='19.42' x2='6.35' y2='17.65'/%3E%3Cline x1='17.65' y1='6.35' x2='19.42' y2='4.58'/%3E%3C/svg%3E\")",
        "theme_btn_hover_bg": "rgba(163, 230, 53, 0.18)",
        "theme_btn_hover_border": "#A3E635",
        "theme_btn_hover_shadow": "0 4px 12px rgba(163, 230, 53, 0.25)",
        "logout_icon_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23A3C2B4' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E\")",
        "logout_icon_hover_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23EF4444' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E\")",
        "logout_btn_hover_bg": "rgba(239, 68, 68, 0.18)",
        "logout_btn_hover_border": "rgba(239, 68, 68, 0.45)",
        "logout_btn_hover_shadow": "0 4px 12px rgba(239, 68, 68, 0.25)",
        "hero_bg": "linear-gradient(135deg, #07382C 0%, #0B4436 45%, #052E24 100%)",
        "hero_overlay": "linear-gradient(to right, #07382C 0%, rgba(7, 56, 44, 0.85) 30%, rgba(7, 56, 44, 0.2) 75%, transparent 100%)",
        "kb_bg": "#0B4436",
        "eco_bg": "#0B4436",
        "arch_stage_bg": "#0B4436",
    },
    "light": {
        "bg_a": "#D3E2D6",
        "bg_b": "#E9F2EA",
        "bg_c": "#E9F2EA",
        "sidebar_a": "#052E24",
        "sidebar_b": "#07382C",
        "surface": "#FFFFFF",
        "surface_elevated": "#FFFFFF",
        "surface_alt": "#E9F2EA",
        "surface_subtle": "#D4E5D8",
        "border": "#C9DCCF",
        "border_soft": "#D8E7DC",
        "border_strong": "#087F5B",
        "text": "#052E24",
        "text_muted": "#64756B",
        "text_dim": "#73867C",
        "accent": "#087F5B",
        "accent_strong": "#052E24",
        "accent_soft": "rgba(8, 127, 91, 0.08)",
        "technical": "#20C997",
        "technical_soft": "rgba(32, 201, 151, 0.10)",
        "success": "#087F5B",
        "success_soft": "rgba(8, 127, 91, 0.10)",
        "warning": "#D97706",
        "warning_soft": "rgba(217, 119, 6, 0.10)",
        "blue": "#20C997",
        "blue_soft": "rgba(32, 201, 151, 0.10)",
        "error": "#DC2626",
        "error_soft": "rgba(220, 38, 38, 0.08)",
        "shadow_sm": "0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)",
        "shadow_md": "0 4px 14px -2px rgba(5, 46, 36, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
        "shadow_lg": "0 10px 24px -4px rgba(5, 46, 36, 0.12), 0 4px 8px -2px rgba(0, 0, 0, 0.04)",
        "code_bg": "#E9F2EA",
        "primary": "#087F5B",
        "secondary": "#20C997",
        "tertiary": "#A3E635",
        "glass_bg": "rgba(255, 255, 255, 0.96)",
        "theme_icon_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23052E24' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z'/%3E%3C/svg%3E\")",
        "theme_icon_hover_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23087F5B' stroke='%23087F5B' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z'/%3E%3C/svg%3E\")",
        "theme_btn_hover_bg": "#D3E2D6",
        "theme_btn_hover_border": "#C9DCCF",
        "theme_btn_hover_shadow": "0 2px 8px rgba(8, 127, 91, 0.12)",
        "logout_icon_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23052E24' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E\")",
        "logout_icon_hover_svg": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23DC2626' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E\")",
        "logout_btn_hover_bg": "#FEE2E2",
        "logout_btn_hover_border": "#FCA5A5",
        "logout_btn_hover_shadow": "0 2px 8px rgba(220, 38, 38, 0.15)",
        "hero_bg": "linear-gradient(135deg, #D3E2D6 0%, #E9F2EA 45%, #D4E5D8 100%)",
        "hero_overlay": "linear-gradient(to right, #D3E2D6 0%, rgba(211, 226, 214, 0.85) 30%, rgba(211, 226, 214, 0.2) 75%, transparent 100%)",
        "kb_bg": "#D4E5D8",
        "eco_bg": "#D4E5D8",
        "arch_stage_bg": "#FFFFFF",
    },
}

CSS_TEMPLATE = Template("""
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important;
}
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: $text !important;
    font-weight: 700 !important;
    letter-spacing: -0.015em !important;
}
.stApp,
div[data-testid="stAppViewContainer"],
section.main {
    background-color: $bg_a !important;
    background: $bg_a !important;
    color: $text;
}
.main .block-container {
    max-width: 1440px !important;
    margin: 0 auto;
    padding-top: 1.5rem !important;
    padding-bottom: 5rem;
}
section[data-testid="stSidebar"] {
    background: $sidebar_a !important;
    border-right: 1.5px solid $border !important;
}
section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.25rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
section[data-testid="stSidebar"][aria-expanded="true"] {
    min-width: 290px !important;
    max-width: 310px !important;
    width: 300px !important;
}
section[data-testid="stSidebar"][aria-expanded="true"] > div:first-child { width: 300px !important; }

/* =============================================================
   FIX 1 — SIDEBAR REOPEN CONTROL
   The "Expand sidebar" button (data-testid="stExpandSidebarButton")
   is rendered inside header[data-testid="stHeader"].
   The previous CSS hid the whole header, removing the reopen button.
   Fix: shrink header to zero height but keep overflow:visible so
   the button can still paint. Hide only other toolbar chrome.
   ============================================================= */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
}
header[data-testid="stHeader"] > div[data-testid="stToolbar"] {
    background: transparent !important;
    overflow: visible !important;
}
header[data-testid="stHeader"] [data-testid="stToolbarActions"],
header[data-testid="stHeader"] [data-testid="stAppDeployButton"],
header[data-testid="stHeader"] [data-testid="stMainMenu"],
header[data-testid="stHeader"] [data-testid="stHeaderActionElements"],
header[data-testid="stHeader"] button[data-testid="stBaseButton-header"],
header[data-testid="stHeader"] span[data-testid="stMainMenu"] { display: none !important; }

/* Explicitly show and style the expand sidebar button */
button[data-testid="stExpandSidebarButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: $surface_elevated !important;
    border: 1.5px solid $border !important;
    border-radius: 10px !important;
    color: $text !important;
    width: 34px !important;
    height: 34px !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    z-index: 99999 !important;
    position: relative !important;
    box-shadow: $shadow_sm !important;
    transition: background-color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease !important;
    margin: 8px 0 0 10px !important;
}
button[data-testid="stExpandSidebarButton"]:hover {
    background: $surface_alt !important;
    border-color: $border_strong !important;
    box-shadow: $shadow_md !important;
}
button[data-testid="stExpandSidebarButton"]:focus-visible {
    outline: 2px solid $technical !important;
    outline-offset: 2px !important;
}
button[data-testid="stExpandSidebarButton"] span,
button[data-testid="stExpandSidebarButton"] svg,
button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
    color: $text !important;
    fill: $text !important;
    font-size: 1.15rem !important;
}

/* Collapse button inside sidebar (when expanded) */
div[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}
div[data-testid="stSidebarCollapseButton"] button,
section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"],
section[data-testid="stSidebar"] button[kind="headerNoPadding"] {
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.22) !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    visibility: visible !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
}
div[data-testid="stSidebarCollapseButton"] button:hover,
section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"]:hover,
section[data-testid="stSidebar"] button[kind="headerNoPadding"]:hover {
    background: rgba(255, 255, 255, 0.18) !important;
    border-color: rgba(255, 255, 255, 0.45) !important;
    transform: scale(1.05) !important;
}
div[data-testid="stSidebarCollapseButton"] button svg,
div[data-testid="stSidebarCollapseButton"] button span,
div[data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] svg,
section[data-testid="stSidebar"] button[kind="headerNoPadding"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 99999 !important;
}

/* Footer */
footer, [data-testid="stFooter"] { display: none !important; height: 0 !important; visibility: hidden !important; }

/* Main Container Padding */
.main .block-container,
div[data-testid="stMainBlockContainer"] {
    padding-top: 1.2rem !important;
    padding-bottom: 5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1680px !important;
}

/* =============================================================
   FIX 2 — CHAT INPUT WIDTH
   st.chat_input() inside a 7/10 column renders inline inside
   stColumn. Use 100% width — no max-width — so it fills the column.
   ============================================================= */
.stBottom, .stBottom > div, .stBottom > div > div,
div[class*="stBottom"], [data-testid="stBottom"],
[data-testid="stBottom"] > div, [data-testid="stChatInputContainer"],
.stChatFloatingInputContainer, section[data-testid="stChatInput"],
div[data-testid="stBottomBlockContainer"], [data-testid="stDecoration"] {
    background: transparent !important;
    background-color: transparent !important;
    border-top: none !important;
    box-shadow: none !important;
}
div[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1.5px solid $border !important;
    border-radius: 18px !important;
    box-shadow: 0 2px 8px -2px rgba(5, 46, 36, 0.06), 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    width: 100% !important;
    margin: 0 0 12px 0 !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #087F5B !important;
    box-shadow: 0 0 0 3px rgba(8, 127, 91, 0.12), 0 3px 12px -2px rgba(8, 127, 91, 0.10) !important;
}
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] > div > div {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    padding: 6px 10px !important;
}
div[data-testid="stChatInput"] textarea,
div[data-testid="stChatInput"] input,
div[data-testid="stChatInput"] [contenteditable="true"] {
    color: #052E24 !important;
    background: transparent !important;
    caret-color: #087F5B !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
}
div[data-testid="stChatInput"] textarea::placeholder,
div[data-testid="stChatInput"] input::placeholder {
    color: #64756B !important;
    opacity: 1 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}
button[data-testid="stChatInputSubmitButton"] {
    background: #087F5B !important;
    color: #FFFFFF !important;
    border-radius: 12px !important;
    border: none !important;
    width: 38px !important;
    height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 6px rgba(5, 46, 36, 0.25) !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
button[data-testid="stChatInputSubmitButton"]:hover {
    background: #052E24 !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(5, 46, 36, 0.30) !important;
    transform: scale(1.05) !important;
}
button[data-testid="stChatInputSubmitButton"]:active {
    transform: scale(0.96) !important;
}
button[data-testid="stChatInputSubmitButton"] svg { fill: #FFFFFF !important; stroke: #FFFFFF !important; }
button[data-testid="stChatInputSubmitButton"]:disabled {
    background: $surface_alt !important;
    opacity: 0.55 !important;
}
button[data-testid="stChatInputSubmitButton"]:disabled svg { fill: $text_dim !important; }

/* Sidebar Logo */
.sidebar-logo-wrap { display: flex; align-items: center; gap: 12px; padding: 4px 0 14px 0; }
.sidebar-logo-icon {
    width: 40px; height: 40px; border-radius: 10px;
    background: #087F5B; color: #A3E635;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem; box-shadow: $shadow_sm; flex-shrink: 0;
}
.sidebar-logo-name { font-size: 1.15rem; font-weight: 700; color: #FFFFFF !important; letter-spacing: -0.01em; line-height: 1.2; }
.sidebar-logo-sub { font-size: 0.72rem; color: #A3C2B4 !important; font-weight: 500; }

/* =============================================================
   FIX 3 + FIX 4 — NAV DECK: Active/hover/focus states
   ============================================================= */
.stitch-nav-item {
    display: flex; align-items: center; gap: 10px; padding: 8px 12px;
    border-radius: 10px; font-size: 0.82rem; font-weight: 500;
    margin-bottom: 4px; transition: all 0.15s ease; text-decoration: none;
}
.stitch-nav-item-active {
    background: #087F5B; color: #FFFFFF !important; font-weight: 600;
    box-shadow: 0 2px 8px -2px rgba(8, 127, 91, 0.45);
}
.stitch-nav-item-idle { color: #A3C2B4; background: transparent; }
.stitch-nav-item-idle:hover { color: #FFFFFF; background: rgba(32, 201, 151, 0.18); }

/* =============================================================
   SIDEBAR NAVIGATION DECK: Dynamic Active-State Highlighting
   ============================================================= */
div.st-key-stitch_nav_deck {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 14px;
}

/* Base style for all sidebar nav buttons */
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"]:not(.st-key-nav_btn_public_landing) div.stButton > button {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    width: 100% !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    font-size: 0.83rem !important;
    min-height: 42px !important;
    height: auto !important;
    gap: 10px !important;
    transition: background-color 0.18s cubic-bezier(0.16, 1, 0.3, 1), color 0.18s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s cubic-bezier(0.16, 1, 0.3, 1), transform 0.18s ease !important;
    white-space: normal !important;
    word-break: break-word !important;
    margin: 0 !important;
}

/* 1. ACTIVE BUTTON STYLE (#087F5B Emerald green, white text/icons, bold) */
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="primary"],
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"] div.stButton > button[kind="primary"],
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"] div.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: #087F5B !important;
    background: #087F5B !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 3px 10px -2px rgba(8, 127, 91, 0.45) !important;
    cursor: default !important;
}
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="primary"]:hover,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"] div.stButton > button[kind="primary"]:hover {
    background-color: #087F5B !important;
    background: #087F5B !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
    box-shadow: 0 4px 14px -2px rgba(8, 127, 91, 0.52) !important;
}
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"] div.stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="primary"] span,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"] div.stButton > button[kind="primary"] span {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    margin: 0 !important;
    line-height: 1.35 !important;
}

/* 2. INACTIVE BUTTON STYLE (Dark forest green friendly, light text, subtle border & hover) */
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="secondary"],
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"]:not(.st-key-nav_btn_public_landing) div.stButton > button[kind="secondary"],
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[data-testid="stBaseButton-secondary"],
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"]:not(.st-key-nav_btn_public_landing) div.stButton > button[data-testid="stBaseButton-secondary"] {
    background-color: transparent !important;
    background: transparent !important;
    color: #A3C2B4 !important;
    font-weight: 500 !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="secondary"]:hover,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"]:not(.st-key-nav_btn_public_landing) div.stButton > button[kind="secondary"]:hover {
    background-color: rgba(255, 255, 255, 0.08) !important;
    background: rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.10) !important;
    transform: translateX(2px) !important;
}
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="secondary"]:focus-visible,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"] div.stButton > button[kind="secondary"]:focus-visible {
    outline: 2px solid rgba(8, 127, 91, 0.5) !important;
    outline-offset: 1px !important;
}
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="secondary"] p,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"]:not(.st-key-nav_btn_public_landing) div.stButton > button[kind="secondary"] p {
    color: #A3C2B4 !important;
    font-weight: 500 !important;
    transition: color 0.18s ease !important;
    margin: 0 !important;
    line-height: 1.35 !important;
}
section[data-testid="stSidebar"] div.st-key-stitch_nav_deck div.stButton > button[kind="secondary"]:hover p,
section[data-testid="stSidebar"] div[class*="st-key-nav_btn_"]:not(.st-key-nav_btn_public_landing) div.stButton > button[kind="secondary"]:hover p {
    color: #FFFFFF !important;
}

/* Sidebar Promo & Version */
.stitch-promo-card {
    background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.10); border-radius: 12px;
    padding: 12px; margin: 16px 0 12px 0; display: flex; align-items: flex-start; gap: 10px;
}
.stitch-promo-icon {
    width: 28px; height: 28px; border-radius: 50%; background: rgba(163, 230, 53, 0.2); color: #A3E635;
    display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; margin-top: 2px;
}
.stitch-promo-title { font-size: 0.78rem; font-weight: 700; color: #FFFFFF; line-height: 1.25; }
.stitch-promo-desc { font-size: 0.7rem; color: #A3C2B4; margin-top: 2px; line-height: 1.35; }
.stitch-version-stamp {
    font-size: 0.7rem; color: #739B8B; line-height: 1.35;
    padding: 2px 4px 10px 4px; display: flex; align-items: center; gap: 6px;
}

/* Sidebar Labels */
.sidebar-nav-label {
    display: flex; align-items: center; gap: 8px; font-size: 0.78rem; font-weight: 700;
    color: $text_muted; text-transform: uppercase; letter-spacing: 0.5px; padding: 10px 2px 6px 2px; margin-top: 6px;
}
.nav-icon { color: $technical; font-size: 0.85rem; width: 15px; text-align: center; flex-shrink: 0; }
.sidebar-subcategory {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
    color: $text_dim; margin-top: 10px; margin-bottom: 4px; padding-left: 2px;
}
.info-row {
    display: flex; align-items: center; gap: 8px; font-size: 0.8rem;
    color: $text_muted; padding: 4px 0 10px 10px;
}
.info-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.info-dot-on { background: $success; }
.info-dot-off { background: $text_dim; }

/* =============================================================
   FIX 3 + FIX 4 — STATUS BADGES
   ============================================================= */
.status-chip-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 2px 0; }
.status-chip {
    display: inline-flex; align-items: center; gap: 5px;
    background: $surface_elevated; border: 1.5px solid $border; border-radius: 8px;
    padding: 4px 9px; font-size: 0.71rem; color: $text_muted;
    font-family: 'JetBrains Mono', monospace; transition: border-color 0.15s ease;
}
.status-chip:hover { border-color: $border_strong; }
.status-chip-live { background: rgba(32, 201, 151, 0.12); border-color: rgba(32, 201, 151, 0.40); color: #087F5B; }
.status-chip-warn { background: rgba(233, 173, 59, 0.12); border-color: rgba(233, 173, 59, 0.42); color: #875D10; }
.status-chip-off { background: $surface_alt; border-color: $border; color: $text_dim; }

/* Top Bar & Topic Pills */
.stitch-top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 14px; margin-bottom: 18px; border-bottom: 1px solid $border; gap: 12px; flex-wrap: wrap;
}
.topic-pills-wrap { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.topic-pill {
    display: inline-flex; align-items: center; gap: 5px; background: $surface_elevated;
    border: 1.5px solid $border; border-radius: 9999px; padding: 4px 12px;
    font-size: 0.78rem; font-weight: 500; color: $text_muted;
    transition: all 0.15s ease; text-decoration: none;
}
.topic-pill:hover { color: $text; background: $surface_alt; border-color: $technical; box-shadow: $shadow_sm; }
.topic-pill-divider { color: $border; font-size: 0.75rem; margin: 0 1px; }

/* =============================================================
   TOP HEADER CONTROLS — UNIFIED FLOATING GLASSMORPHISM PILL
   ============================================================= */
div.st-key-stitch_top_nav {
    border-bottom: 1.5px solid $border !important;
    padding-bottom: 10px !important;
    margin-bottom: 20px !important;
}
div.st-key-stitch_top_nav > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
}
div.st-key-stitch_top_nav > div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
    justify-content: flex-start !important;
}
div.st-key-stitch_top_nav div[data-testid="stMarkdown"],
div.st-key-stitch_top_nav div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Top Nav Brand Header */
.top-nav-brand-wrap {
    display: inline-flex !important;
    align-items: center !important;
    gap: 12px !important;
    user-select: none !important;
    min-height: 42px !important;
}
.top-nav-logo-img {
    width: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    object-fit: cover !important;
    box-shadow: 0 2px 6px rgba(5, 46, 36, 0.12) !important;
    border: 1.5px solid $border !important;
    flex-shrink: 0 !important;
    display: block !important;
}
.top-nav-logo-fallback {
    width: 34px !important;
    height: 34px !important;
    border-radius: 10px !important;
    background: $surface_elevated !important;
    border: 1.5px solid $border !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.15rem !important;
    flex-shrink: 0 !important;
}
.top-nav-brand-title {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
    color: $text !important;
    line-height: 1.1 !important;
    text-transform: uppercase !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* User Profile Chip: Avatar + Role Pill Badge */
.user-profile-chip {
    display: inline-flex !important;
    align-items: center !important;
    gap: 7px !important;
    padding: 2px 4px 2px 2px !important;
    text-decoration: none !important;
    user-select: none !important;
}

.user-avatar-badge {
    position: relative !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    border-radius: 50% !important;
    background: #052E24 !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    cursor: default !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    flex-shrink: 0 !important;
    margin: 0 !important;
    line-height: 1 !important;
}
.user-avatar-badge:hover {
    border-color: #087F5B !important;
    box-shadow: 0 0 0 2px rgba(8, 127, 91, 0.2), 0 3px 8px rgba(5, 46, 36, 0.25) !important;
    transform: scale(1.05) !important;
}

.user-status-dot {
    position: absolute !important;
    bottom: -1px !important;
    right: -1px !important;
    width: 8px !important;
    height: 8px !important;
    border-radius: 50% !important;
    background: #20C997 !important;
    border: 1.5px solid $surface_elevated !important;
    box-shadow: 0 0 4px rgba(32, 201, 151, 0.8) !important;
}

.user-chip-text {
    display: flex !important;
    align-items: center !important;
}

.user-chip-role {
    font-size: 0.70rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #087F5B !important;
    background: $accent_soft !important;
    padding: 3px 8px !important;
    border-radius: 9999px !important;
    border: 1px solid $border !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
}

/* Unified Floating Glassmorphism Pill Container */
div.st-key-stitch_header_cluster {
    background: $glass_bg !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1.5px solid $border !important;
    border-radius: 9999px !important;
    padding: 4px 8px 4px 6px !important;
    box-shadow: 0 2px 10px -2px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    margin-left: auto !important;
    width: fit-content !important;
    min-height: 42px !important;
    box-sizing: border-box !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
div.st-key-stitch_header_cluster:hover {
    border-color: $technical !important;
    box-shadow: 0 4px 16px -2px rgba(8, 127, 91, 0.12) !important;
}

/* Horizontal alignment & 6px gap between controls */
div.st-key-stitch_header_cluster div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    width: auto !important;
    flex-wrap: nowrap !important;
    margin: 0 !important;
    padding: 0 !important;
}

div.st-key-stitch_header_cluster div[data-testid="stColumn"] {
    width: auto !important;
    min-width: 32px !important;
    flex: 0 0 auto !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Vertical divider after user badge column */
div.st-key-stitch_header_cluster div[data-testid="stColumn"]:first-child {
    border-right: 1px solid $border !important;
    padding-right: 8px !important;
    margin-right: 2px !important;
}

div.st-key-stitch_header_cluster div[data-testid="stMarkdown"],
div.st-key-stitch_header_cluster div[data-testid="stMarkdownContainer"],
div.st-key-stitch_header_cluster div[data-testid="stMarkdownContainer"] p {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
}

div.st-key-stitch_header_cluster div.stButton {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 34px !important;
    height: 34px !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Standardized 34px Circular Buttons with Direct Background Icon (guaranteed dead-center) */
div.st-key-stitch_top_nav button,
div.st-key-stitch_header_cluster button,
div.st-key-theme_toggle_main button,
div.st-key-top_sign_out_btn button {
    background-color: $surface_elevated !important;
    border: 1px solid $border !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    padding: 0 !important;
    border-radius: 50% !important;
    min-height: 34px !important;
    height: 34px !important;
    width: 34px !important;
    min-width: 34px !important;
    max-width: 34px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    margin: 0 !important;
    cursor: pointer !important;
    position: relative !important;
    font-size: 0 !important;
    color: transparent !important;
    line-height: 0 !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
    background-repeat: no-repeat !important;
    background-position: center center !important;
    background-size: 18px 18px !important;
}

/* Hide all children inside the buttons (eliminates any displacement) */
div.st-key-theme_toggle_main button *,
div.st-key-top_sign_out_btn button * {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    font-size: 0 !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 0 !important;
    border: none !important;
}

/* Remove any pseudo-elements */
div.st-key-theme_toggle_main button::after,
div.st-key-top_sign_out_btn button::after,
div.st-key-theme_toggle_main button::before,
div.st-key-top_sign_out_btn button::before {
    display: none !important;
    content: none !important;
}

/* Theme Toggle Button Icon & Hover */
div.st-key-theme_toggle_main button {
    background-image: $theme_icon_svg !important;
}
div.st-key-theme_toggle_main button:hover {
    background-color: $theme_btn_hover_bg !important;
    background-image: $theme_icon_hover_svg !important;
    border-color: $theme_btn_hover_border !important;
    box-shadow: $theme_btn_hover_shadow !important;
    transform: scale(1.08) !important;
}

/* Logout / Exit Door Button Icon & Hover */
div.st-key-top_sign_out_btn button {
    background-image: $logout_icon_svg !important;
}
div.st-key-top_sign_out_btn button:hover {
    background-color: $logout_btn_hover_bg !important;
    background-image: $logout_icon_hover_svg !important;
    border-color: $logout_btn_hover_border !important;
    box-shadow: $logout_btn_hover_shadow !important;
    transform: scale(1.08) !important;
}

div.st-key-stitch_header_cluster button:active {
    transform: scale(0.94) !important;
}

/* =============================================================
   FIX 3 — HERO: Stronger shadow, more depth
   ============================================================= */
.stitch-hero {
    position: relative; overflow: hidden; border-radius: 24px;
    background: $hero_bg;
    border: 1.5px solid $border; padding: 28px 32px; box-shadow: $shadow_md;
    margin-bottom: 24px; min-height: 230px;
}
.stitch-hero-bg-img {
    position: absolute; right: 0; top: 0; bottom: 0; width: 52%;
    pointer-events: none; overflow: hidden; z-index: 1;
}
.stitch-hero-bg-img img { width: 100%; height: 100%; object-fit: cover; object-position: right center; }
.stitch-hero-overlay {
    position: absolute; inset: 0;
    background: $hero_overlay;
    z-index: 2;
}
.stitch-hero-content { position: relative; z-index: 3; max-width: 540px; }
.hero-pill {
    display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px;
    border-radius: 9999px; background: rgba(163, 230, 53, 0.15); color: #052E24;
    font-size: 0.74rem; font-weight: 700; border: 1px solid rgba(8, 127, 91, 0.22); margin-bottom: 12px;
}
.hero-title { font-size: 2.1rem; font-weight: 800; color: $text; line-height: 1.15; letter-spacing: -0.025em; margin: 0; }
.hero-sub { font-size: 1rem; font-weight: 700; color: $text; margin-top: 4px; }
.hero-desc { font-size: 0.84rem; color: $text_muted; line-height: 1.55; margin-top: 8px; max-width: 480px; }
.hero-chips-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.hero-chip {
    display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px;
    border-radius: 9999px; background: $surface_elevated; border: 1.5px solid $border;
    font-size: 0.74rem; font-weight: 600; color: $text; box-shadow: $shadow_sm;
}

/* =============================================================
   FIX 3 + FIX 5 — PROMPT STARTER CARDS: White, clearly elevated
   ============================================================= */
.prompt-grid-header {
    display: flex; align-items: center; gap: 8px; font-size: 1.15rem; font-weight: 800; color: $text; margin-bottom: 4px;
}
.prompt-grid-sub { font-size: 0.82rem; color: $text_muted; margin-bottom: 14px; }
div.st-key-starter_card_container div.stButton > button {
    background: $surface_elevated !important; border: 1.5px solid $border !important;
    border-radius: 16px !important; padding: 14px 16px !important; text-align: left !important;
    box-shadow: $shadow_sm !important; min-height: 86px !important; display: flex !important;
    flex-direction: column !important; align-items: flex-start !important; justify-content: center !important;
    transition: all 0.2s ease !important; margin-bottom: 10px !important;
}
div.st-key-starter_card_container div.stButton > button:hover {
    border-color: #087F5B !important; box-shadow: $shadow_md !important;
    transform: translateY(-2px) !important;
}
div.st-key-starter_card_container div.stButton > button:focus-visible {
    outline: 2px solid #087F5B !important; outline-offset: 2px !important;
}
div.st-key-starter_card_container div.stButton > button p { margin: 0 !important; color: $text !important; line-height: 1.4 !important; }

/* Right Rail */
.right-rail-wrap { display: flex; flex-direction: column; gap: 14px; }
.kb-status-card {
    background: $kb_bg !important;
    border: 1.5px solid $border !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    box-shadow: $shadow_sm !important;
    transition: all 0.18s ease !important;
}
.kb-status-card:hover {
    border-color: $accent !important;
    box-shadow: $shadow_md !important;
}
.kb-status-title {
    font-size: 0.88rem !important;
    font-weight: 800 !important;
    color: $text !important;
    letter-spacing: -0.01em !important;
}
.kb-status-sub {
    font-size: 0.74rem !important;
    color: $text_muted !important;
    font-weight: 600 !important;
    margin-top: 2px !important;
}
.kb-status-icon-wrap {
    width: 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    background: #087F5B !important;
    color: #FFFFFF !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.05rem !important;
    box-shadow: 0 2px 6px rgba(5, 46, 36, 0.25) !important;
}
.beacon-dot { width: 10px; height: 10px; border-radius: 50%; background: #20C997; display: inline-block; box-shadow: 0 0 0 3px rgba(32, 201, 151, 0.32); }
.quick-stats-card { background: $surface_elevated; border: 1.5px solid $border; border-radius: 14px; padding: 15px; box-shadow: $shadow_sm; }
.quick-stats-title { font-size: 0.82rem; font-weight: 700; color: $text; margin-bottom: 10px; }
.quick-stat-box {
    background: $surface_alt; border: 1px solid $border; border-radius: 9px; padding: 9px 10px;
    display: flex; align-items: center; gap: 8px; transition: border-color 0.15s ease;
}
.quick-stat-box:hover { border-color: $border_strong; }
.quick-stat-val { font-size: 0.88rem; font-weight: 700; color: $text; line-height: 1.1; }
.quick-stat-lbl { font-size: 0.68rem; color: $text_muted; }
.suggested-rail-card { background: $surface_elevated; border: 1.5px solid $border; border-radius: 14px; padding: 14px; box-shadow: $shadow_sm; }
.suggested-rail-title { font-size: 0.82rem; font-weight: 700; color: $text; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.eco-banner-card {
    border-radius: 14px; border: 1.5px solid $border;
    background: $eco_bg;
    padding: 13px 15px; display: flex; align-items: center; gap: 10px;
}

/* Calculator Card */
.calc-card { background: $surface_elevated; border: 1.5px solid $border; border-radius: 14px; padding: 18px; margin-top: 8px; box-shadow: $shadow_sm; }
.calc-label { font-size: 0.7rem; text-transform: uppercase; color: $text_muted; font-weight: 700; letter-spacing: 0.5px; }
.calc-val { font-size: 1.4rem; font-weight: 700; color: $accent; margin-top: 4px; }
.calc-detail { font-size: 0.8rem; color: $text_muted; line-height: 1.8; margin-top: 10px; }
.calc-payback { color: $technical; font-weight: 700; }
.cap-badge { font-size: 0.65rem; background: $accent_soft; color: $accent; border: 1px solid $accent; border-radius: 4px; padding: 2px 6px; margin-left: 8px; vertical-align: middle; font-weight: 600; }

/* =============================================================
   FIX 3 + FIX 4 — GLOBAL BUTTONS: Distinct states
   ============================================================= */
div.stButton > button {
    width: 100%; background: $surface_elevated; color: $text;
    border: 1.5px solid $border; border-radius: 9px; padding: 8px 14px;
    font-size: 0.82rem; font-weight: 600; text-align: center;
    transition: all 0.15s ease; box-shadow: $shadow_sm;
}
div.stButton > button:hover { background: $surface_alt; color: $text; border-color: $border_strong; box-shadow: $shadow_md; }
div.stButton > button:focus-visible { outline: 2px solid $technical; outline-offset: 2px; }
div.stButton > button:active { transform: scale(0.98); box-shadow: none; }

/* Chat Messages */
div[data-testid="stChatMessage"] {
    background: $surface_elevated; border: 1px solid $border; border-radius: 12px;
    border-left: 3.5px solid $border; padding: 12px 16px 12px 20px; margin-bottom: 14px; box-shadow: $shadow_sm;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]),
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) { border-left-color: $text_muted; background: $surface_alt; }
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]),
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) { border-left-color: #087F5B; background: #FFFFFF; }
div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"],
div[data-testid="chatAvatarIcon-user"], div[data-testid="chatAvatarIcon-assistant"] { display: none !important; }

/* Source & Compare Cards */
.source-card { background: $surface_elevated; border: 1.5px solid $border; border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; box-shadow: $shadow_sm; transition: border-color 0.15s ease; }
.source-card:hover { border-color: $border_strong; }
.source-card-title { font-size: 0.8rem; font-weight: 700; color: $text; margin-bottom: 5px; }
.source-card-snippet { font-size: 0.78rem; color: $text_muted; line-height: 1.55; }
.source-card-rank { font-size: 0.7rem; font-weight: 600; color: $accent; margin-left: 6px; }
.compare-card { background: $surface_elevated; border: 1.5px solid $border; border-radius: 12px; padding: 14px; margin-bottom: 8px; box-shadow: $shadow_sm; }
.compare-card-rag { border-top: 3px solid $accent; }
.compare-card-direct { border-top: 3px solid #EF4444; }
.compare-card-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.compare-card-label-rag { color: $accent; }
.compare-card-label-direct { color: #EF4444; }
.compare-warning { background: $surface_alt; border: 1px solid $border; border-radius: 8px; padding: 10px 12px; font-size: 0.76rem; color: $text_muted; margin-top: 6px; }

/* Expanders */
.stExpander { border: none !important; border-radius: 0 !important; background: transparent !important; margin-top: 0 !important; box-shadow: none !important; }
section[data-testid="stSidebar"] .stExpander { border-bottom: 1px solid $border !important; }
.stExpander summary { font-weight: 600 !important; color: $text !important; font-size: 0.82rem !important; padding: 10px 2px !important; }
.stExpander summary:hover { color: $accent !important; }
[data-testid="stExpanderDetails"] { padding-top: 4px !important; }

/* Pipeline & Architecture */
.pipeline-chip-row { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin: 10px 0; }
.pipeline-chip { background: $surface_elevated; border: 1.5px solid $border; border-radius: 7px; padding: 4px 10px; font-size: 0.72rem; color: $text; font-weight: 600; }
.pipeline-arrow { color: $text_dim; font-size: 0.75rem; }
.arch-step { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid $border; }
.arch-step:last-child { border-bottom: none; }
.arch-num { min-width: 26px; height: 26px; background: $surface_elevated; border: 1.5px solid $border; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.76rem; font-weight: 700; color: $accent; }
.arch-content { font-size: 0.8rem; color: $text_muted; line-height: 1.5; }
.arch-content b { color: $text; }
.arch-why { font-size: 0.75rem; color: $text_dim; line-height: 1.5; margin-top: 6px; padding-left: 10px; border-left: 2px solid $border; }

/* Eval Stats */
.eval-summary-row { display: flex; gap: 12px; margin: 12px 0 20px 0; flex-wrap: wrap; }
.eval-stat { flex: 1; min-width: 120px; background: $surface_elevated; border: 1.5px solid $border; border-radius: 12px; padding: 14px; text-align: center; box-shadow: $shadow_sm; transition: box-shadow 0.15s ease, border-color 0.15s ease; }
.eval-stat:hover { border-color: $border_strong; box-shadow: $shadow_md; }
.eval-stat-val { font-size: 1.4rem; font-weight: 700; color: $text; }
.eval-stat-lbl { font-size: 0.68rem; color: $text_muted; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
.eval-row { display: flex; align-items: flex-start; gap: 12px; background: $surface_elevated; border: 1.5px solid $border; border-radius: 9px; padding: 10px 12px; margin-bottom: 6px; transition: border-color 0.15s ease; }
.eval-row:hover { border-color: $border_strong; }
.eval-tag { font-size: 0.68rem; font-weight: 700; border-radius: 5px; padding: 3px 8px; white-space: nowrap; border: 1px solid transparent; }
.eval-tag-correct { background: $accent_soft; color: $accent; border-color: $accent; }
.eval-tag-partial { background: $technical_soft; color: $technical; border-color: $technical; }
.eval-tag-declined { background: $surface_alt; color: $text_muted; border-color: $border; }
.eval-q { font-size: 0.82rem; color: $text; font-weight: 600; }
.eval-note { font-size: 0.76rem; color: $text_muted; margin-top: 2px; }

/* File Uploader */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] > div,
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploaderDropzone"] {
    background: #FFFFFF !important;
    border: 2px dashed $border !important;
    border-radius: 14px !important;
    color: #64756B !important;
    transition: all 0.18s ease !important;
}
div[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #087F5B !important;
    background: $surface_alt !important;
}
div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
    background: #087F5B !important;
    color: #FFFFFF !important;
    border: 1.5px solid #087F5B !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 8px 18px !important;
    box-shadow: 0 2px 8px rgba(8, 127, 91, 0.25) !important;
    transition: all 0.18s ease !important;
}
div[data-testid="stFileUploader"] button:hover,
div[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]:hover {
    background: #052E24 !important;
    border-color: #052E24 !important;
    box-shadow: 0 4px 14px rgba(5, 46, 36, 0.35) !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stFileUploader"] button:focus-visible,
div[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]:focus-visible {
    outline: 2px solid #087F5B !important;
    outline-offset: 2px !important;
}

/* Clean Energy Card */
.eco-artwork-card {
    position: relative; overflow: hidden; border-radius: 16px;
    border: 1.5px solid $border;
    background: linear-gradient(135deg, $accent_soft 0%, $surface_alt 100%);
    padding: 14px 16px; min-height: 80px; display: flex; align-items: center; margin-top: 10px; box-shadow: $shadow_sm;
}
.eco-artwork-content { display: flex; align-items: center; gap: 12px; position: relative; z-index: 2; }
.eco-artwork-icon { width: 32px; height: 32px; border-radius: 50%; background: #087F5B; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 15px; box-shadow: 0 2px 6px rgba(8, 127, 91, 0.30); flex-shrink: 0; }
.eco-artwork-title { font-size: 0.85rem; font-weight: 700; color: #052E24; line-height: 1.2; }
.eco-artwork-sub { font-size: 0.74rem; font-weight: 600; color: #087F5B; margin-top: 1px; }

/* =============================================================
   FIX 3 + FIX 4 — STITCH PAGE SYSTEM: Elevated cards, strong depth
   ============================================================= */
.stitch-page-wrap { margin-top: 8px; margin-bottom: 32px; }
.stitch-breadcrumbs { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: $text_dim; margin-bottom: 6px; display: flex; align-items: center; gap: 6px; }
.stitch-breadcrumbs span.crumb-active { color: $accent; }
.stitch-page-title-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 20px; }
.stitch-page-title { font-size: 1.85rem; font-weight: 800; color: $text; line-height: 1.2; letter-spacing: -0.02em; }
.stitch-page-desc { font-size: 0.92rem; color: $text_muted; max-width: 780px; line-height: 1.55; margin-top: 6px; }

.stitch-kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }
@media (max-width: 1024px) { .stitch-kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.stitch-kpi-card {
    background: $surface_elevated !important;
    border: 1.5px solid $border !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    min-height: 126px !important;
    height: 100% !important;
    box-sizing: border-box !important;
    transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.18s ease !important;
}
.stitch-kpi-card:hover {
    border-color: $border_strong !important;
    box-shadow: 0 4px 14px -2px rgba(5, 46, 36, 0.08) !important;
    transform: translateY(-2px) !important;
}
.stitch-kpi-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.stitch-kpi-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #64756B; }
.stitch-kpi-icon { width: 34px; height: 34px; border-radius: 9px; background: $surface_alt; border: 1px solid $border; color: #087F5B; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.stitch-kpi-val { font-size: 1.65rem; font-weight: 800; color: #052E24; line-height: 1.1; letter-spacing: -0.015em; }
.stitch-kpi-sub { font-size: 0.72rem; color: #64756B; margin-top: 4px; line-height: 1.4; font-weight: 500; }

.stitch-card { background: $surface_elevated !important; border: 1.5px solid $border !important; border-radius: 16px !important; padding: 22px 24px !important; box-shadow: $shadow_sm !important; margin-bottom: 20px !important; box-sizing: border-box !important; transition: box-shadow 0.15s ease, border-color 0.15s ease !important; }
.stitch-card:hover { border-color: $border_strong; box-shadow: $shadow_md; }
.stitch-card-title { font-size: 1.05rem; font-weight: 700; color: $text; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; }
.stitch-card-sub { font-size: 0.8rem; color: $text_muted; line-height: 1.45; margin-bottom: 14px; }

.stitch-table-wrap { width: 100%; overflow-x: auto; border-radius: 12px; border: 1.5px solid $border; }
.stitch-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; background: $surface_elevated; }
.stitch-table th { background: $surface_alt; color: $text_muted; font-weight: 700; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.6px; padding: 10px 14px; text-align: left; border-bottom: 1.5px solid $border; }
.stitch-table td { padding: 12px 14px; border-bottom: 1px solid $border_soft; color: $text; vertical-align: middle; }
.stitch-table tr:hover td { background: $surface_subtle; }
.format-badge { display: inline-block; padding: 2px 7px; border-radius: 5px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; }
.format-badge-pdf { background: rgba(220, 38, 38, 0.12); color: #B91C1C; }
.format-badge-txt { background: rgba(59, 130, 246, 0.12); color: #1D4ED8; }

.stitch-qcard { background: $surface_elevated; border: 1.5px solid $border; border-radius: 14px; padding: 18px; box-shadow: $shadow_sm; display: flex; flex-direction: column; justify-content: space-between; height: 100%; transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease; }
.stitch-qcard:hover { border-color: $border_strong; transform: translateY(-2px); box-shadow: $shadow_md; }
.stitch-qcard-tag { font-size: 0.7rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; display: inline-block; margin-bottom: 10px; align-self: flex-start; }
.stitch-qcard-title { font-size: 0.92rem; font-weight: 700; color: $text; line-height: 1.35; margin-bottom: 8px; }
.stitch-qcard-desc { font-size: 0.78rem; color: $text_muted; line-height: 1.45; margin-bottom: 14px; flex-grow: 1; }

.stitch-optimal-card { background: linear-gradient(145deg, #087F5B 0%, #052E24 100%); border-radius: 16px; padding: 22px; color: #FFFFFF; box-shadow: 0 6px 20px -4px rgba(5, 46, 36, 0.38); margin-bottom: 16px; }
.stitch-optimal-kw { font-size: 2.4rem; font-weight: 800; line-height: 1.1; color: #FFFFFF; margin: 8px 0; }

/* Suggested Questions Rail Container & Centered Buttons */
div[class*="st-key-suggested_rail_box"] {
    background: $surface_elevated !important;
    border: 1.5px solid $border !important;
    border-radius: 14px !important;
    padding: 16px 14px 12px 14px !important;
    box-shadow: $shadow_sm !important;
    margin-bottom: 14px !important;
    box-sizing: border-box !important;
}
.suggested-rail-header,
.suggested-rail-title {
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    color: $text !important;
    margin: 0 auto 12px auto !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    text-align: center !important;
    width: 100% !important;
}
div.st-key-suggested_rail_box div.stButton {
    width: 100% !important;
    margin-bottom: 8px !important;
}
div.st-key-suggested_rail_box div.stButton:last-child {
    margin-bottom: 0 !important;
}
div.st-key-suggested_rail_box div.stButton > button {
    background: $surface_alt !important;
    border: 1.5px solid $border !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
    text-align: center !important;
    color: $text !important;
    font-size: 0.79rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    min-height: 40px !important;
    height: auto !important;
    margin: 0 !important;
    transition: all 0.15s ease !important;
    justify-content: center !important;
    align-items: center !important;
    display: flex !important;
    width: 100% !important;
    line-height: 1.35 !important;
}
div.st-key-suggested_rail_box div.stButton > button:hover {
    background: $surface_elevated !important;
    border-color: $accent !important;
    color: $accent !important;
    box-shadow: $shadow_sm !important;
    transform: translateY(-1px) !important;
}
div.st-key-suggested_rail_box div.stButton > button p,
div.st-key-suggested_rail_box div.stButton > button span {
    text-align: center !important;
    justify-content: center !important;
    align-items: center !important;
    display: block !important;
    margin: 0 auto !important;
    width: 100% !important;
    white-space: normal !important;
    word-break: normal !important;
    color: $text !important;
    line-height: 1.35 !important;
}
div.st-key-suggested_rail_box div.stButton > button:hover p,
div.st-key-suggested_rail_box div.stButton > button:hover span {
    color: $accent !important;
}

/* Input focus states */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] select,
div[data-testid="stTextArea"] textarea {
    border: 1.5px solid $border !important; border-radius: 9px !important;
    background: $surface_elevated !important; color: $text !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #087F5B !important;
    box-shadow: 0 0 0 3px rgba(8, 127, 91, 0.15) !important;
    outline: none !important;
}

/* =============================================================
   FIX 5 — COMPARE MODE CARD (compact, balanced)
   ============================================================= */
.compare-mode-card { background: #FFFFFF !important; border: 1.5px solid $border !important; border-radius: 14px; padding: 14px 18px; margin-bottom: 18px; display: flex; align-items: center; gap: 14px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); }
.compare-mode-icon { font-size: 1.4rem; flex-shrink: 0; }
.compare-mode-body { flex: 1; }
.compare-mode-title { font-size: 0.9rem; font-weight: 700; color: $text; display: flex; align-items: center; gap: 8px; }
.compare-badge { font-size: 0.65rem; font-weight: 700; padding: 2px 7px; border-radius: 5px; letter-spacing: 0.3px; text-transform: uppercase; }
.compare-badge-active { background: $success_soft; color: $success; border: 1px solid $success; }
.compare-badge-off { background: $surface_alt; color: $text_dim; border: 1px solid $border; }
.compare-mode-desc { font-size: 0.78rem; color: $text_muted; margin-top: 3px; }

/* =============================================================
   ARCHITECTURE 5 STAGES & CONTAINER CARD STYLING
   ============================================================= */
.arch-stage-card {
    background: $arch_stage_bg !important;
    border: 1.5px solid $border !important;
    border-radius: 14px !important;
    padding: 16px 14px !important;
    min-height: 154px !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    box-shadow: $shadow_sm !important;
    box-sizing: border-box !important;
    transition: all 0.18s ease !important;
}
.arch-stage-card:hover {
    border-color: $accent !important;
    box-shadow: $shadow_md !important;
    transform: translateY(-2px) !important;
}
.arch-stage-num {
    font-size: 0.68rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    background: #087F5B !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    display: inline-block !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 6px !important;
}
.arch-stage-title {
    font-size: 0.9rem !important;
    font-weight: 800 !important;
    color: $text !important;
    line-height: 1.25 !important;
    margin-bottom: 4px !important;
}
.arch-stage-desc {
    font-size: 0.73rem !important;
    color: $text_muted !important;
    line-height: 1.45 !important;
    flex-grow: 1 !important;
}
.arch-stage-footer {
    margin-top: 10px !important;
    font-size: 0.69rem !important;
    color: $accent !important;
    font-weight: 600 !important;
    border-top: 1px solid $border !important;
    padding-top: 6px !important;
}

/* Styled Container Cards */
div[class*="st-key-kb_corpus_card"],
div[class*="st-key-kb_inspect_card"],
div[class*="st-key-upload_corpus_card"],
div[class*="st-key-status_pipeline_card"],
div[class*="st-key-calc_inputs_card"],
div[class*="st-key-settings_chunk_card"],
div[class*="st-key-settings_retrieval_card"],
div[class*="st-key-settings_loop_card"],
div[class*="st-key-settings_model_card"],
div[class*="st-key-eval_log_card"] {
    background: $surface_elevated !important;
    border: 1.5px solid $border !important;
    border-radius: 16px !important;
    padding: 22px 24px !important;
    box-shadow: $shadow_sm !important;
    margin-bottom: 20px !important;
    box-sizing: border-box !important;
}

/* Compare Mode Box */
.compare-mode-card {
    background: $surface_elevated !important;
    border: 1.5px solid $border !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    margin-bottom: 14px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
    box-shadow: $shadow_sm !important;
}
/* =============================================================
   LAYOUT CONSISTENCY & ROW ALIGNMENT SYSTEM
   ============================================================= */
div[data-testid="stHorizontalBlock"] {
    gap: 18px !important;
    align-items: stretch !important;
}
div.st-key-stitch_header_cluster div[data-testid="stHorizontalBlock"] {
    gap: 6px !important;
    align-items: center !important;
}
div.st-key-stitch_top_nav div[data-testid="stHorizontalBlock"] {
    gap: 12px !important;
    align-items: center !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    display: flex !important;
    flex-direction: column !important;
    justify-content: stretch !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    height: 100% !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div[data-testid="stMarkdown"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    height: 100% !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div[data-testid="stMarkdown"] > div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    height: 100% !important;
}
""")

def get_css(theme_name: str) -> str:
    T = THEMES[theme_name]
    _css = CSS_TEMPLATE.substitute(**T)
    return _css

