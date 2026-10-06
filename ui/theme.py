from string import Template

THEMES = {
    "dark": {
        "bg_a": "#12161B", "bg_b": "#12161B", "bg_c": "#12161B",
        "sidebar_a": "#1A1E24", "sidebar_b": "#1A1E24",
        "surface": "#232830", "surface_alt": "#1A1E24",
        "border": "#2D3748", "border_soft": "#2D3748",
        "text": "#F8FAFC", "text_muted": "#94A3B8", "text_dim": "#64748B",
        "accent": "#10B981", "accent_strong": "#059669", "accent_soft": "rgba(16,185,129,0.1)",
        "technical": "#3B82F6", "technical_soft": "rgba(59,130,246,0.1)",
        "success": "#10B981", "success_soft": "rgba(16,185,129,0.1)",
        "error": "#EF4444", "error_soft": "rgba(239,68,68,0.1)",
        "shadow_sm": "transparent", "shadow_md": "transparent",
        "code_bg": "#12161B",
    },
    "light": {
        "bg_a": "#F8FAFC", "bg_b": "#F8FAFC", "bg_c": "#F8FAFC",
        "sidebar_a": "#FFFFFF", "sidebar_b": "#FFFFFF",
        "surface": "#FFFFFF", "surface_alt": "#F1F5F9",
        "border": "#CBD5E1", "border_soft": "#E2E8F0",
        "text": "#0F172A", "text_muted": "#475569", "text_dim": "#64748B",
        "accent": "#10B981", "accent_strong": "#059669", "accent_soft": "rgba(16,185,129,0.1)",
        "technical": "#3B82F6", "technical_soft": "rgba(59,130,246,0.1)",
        "success": "#10B981", "success_soft": "rgba(16,185,129,0.1)",
        "error": "#EF4444", "error_soft": "rgba(239,68,68,0.1)",
        "shadow_sm": "transparent", "shadow_md": "transparent",
        "code_bg": "#F1F5F9",
    },
}

CSS_TEMPLATE = Template("""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
.stApp {
    background: $bg_a;
    color: $text;
}
.main .block-container {
    max-width: 1100px;
    margin: 0 auto;
    padding-top: 2rem;
    padding-bottom: 6rem;
}
section[data-testid="stSidebar"] {
    background: $sidebar_a !important;
    border-right: 1px solid $border !important;
}
/* Full height sidebar */
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
}

/* Only lock width when sidebar is OPEN */
section[data-testid="stSidebar"][aria-expanded="true"] {
    min-width: 320px !important;
    max-width: 340px !important;
    width: 330px !important;
}
section[data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
    width: 330px !important;
}

.sidebar-logo-wrap { display:flex; align-items:center; gap:12px; padding:4px 0 16px 0; }
.sidebar-logo-img {
    width: 48px !important;
    height: 48px !important;
    border-radius: 4px !important;
    object-fit: cover;
}
.sidebar-logo-name { font-size:1.1rem; font-weight:700; color:$text; line-height:1.2; }
.sidebar-logo-sub  { font-size:0.7rem; color:$accent; font-weight:600; }

.sidebar-nav-label { display:flex; align-items:center; gap:9px; font-size:0.85rem; font-weight:600; color:$text; padding:12px 2px 8px 2px; border-bottom:1px solid $border; margin-top:8px;}
.nav-icon { color:$technical; font-size:0.9rem; width:15px; text-align:center; flex-shrink:0; }

.sidebar-subcategory { font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:$text_muted; margin-top:12px; margin-bottom:6px; padding-left:2px; }

.status-online  { color:$success; font-weight:700; font-size:0.82rem; }
.status-offline { color:$error; font-weight:700; font-size:0.82rem; }
.kb-doc-list { margin-top:4px; font-size:0.75rem; color:$text_muted; line-height:1.6; }

.info-row { display:flex; align-items:center; gap:8px; font-size:0.8rem; color:$text_muted; padding:4px 0 12px 24px; }
.info-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.info-dot-on  { background:$success; }
.info-dot-off { background:$text_dim; }

.status-chip-row { display:flex; flex-wrap:wrap; gap:6px; margin:4px 0 2px 0; }
.status-chip { display:inline-flex; align-items:center; gap:5px; background:$surface; border:1px solid $border; border-radius:4px; padding:4px 9px; font-size:0.71rem; color:$text_muted; font-family:'JetBrains Mono', monospace; }

.ctx-label { font-size:0.66rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:$text_dim; margin:2px 0 6px 0; }
.ctx-chip-row { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:10px; }
.ctx-chip { background:$surface; border:1px solid $border; border-radius:4px; padding:4px 10px; font-size:0.74rem; color:$text_muted; }
.ctx-chip-rank { color:$technical; font-weight:700; }

.calc-card { background:$surface; border:1px solid $border; border-radius:4px; padding:16px; margin-top:8px; }
.calc-label { font-size:0.7rem; text-transform:uppercase; color:$text_muted; font-weight:700; letter-spacing:0.5px; }
.calc-val   { font-size:1.4rem; font-weight:700; color:$text; margin-top:4px; }
.calc-detail { font-size:0.8rem; color:$text_muted; line-height:1.8; margin-top:12px; }
.calc-payback { color:$accent; font-weight:700; }
.cap-badge { font-size:0.65rem; background:$accent_soft; color:$accent; border:1px solid $accent; border-radius:2px; padding:2px 6px; margin-left:8px; vertical-align:middle; font-weight:600;}

div.stButton > button { width:100%; background:$surface; color:$text; border:1px solid $border; border-radius:4px; padding:10px 16px; font-size:0.85rem; font-weight:600; text-align:center; }
div.stButton > button:hover { background:$border; color:$text; border-color:$border; }

.top-bar { display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid $border; padding-bottom:16px; margin-bottom:24px; gap:16px; flex-wrap:wrap; }
.top-bar-title { font-size: 1.5rem; font-weight: 700; color: $text; letter-spacing: -0.2px; line-height: 1.2; }
.top-bar-tagline { font-size:0.85rem; color:$text_muted; font-weight:500; margin-top:2px; }
.kb-pill { display:inline-flex; align-items:center; gap:8px; border:1px solid $border; border-radius:4px; padding:6px 14px; font-size:0.8rem; font-weight:600; background:$surface; }
.kb-pill-dot { width:8px; height:8px; border-radius:50%; }

.badge-row { display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-top:8px; }
.badge { display:inline-flex; align-items:center; gap:5px; border-radius:4px; padding:4px 10px; font-size:0.75rem; font-weight:600; border:1px solid $border; }
.badge-green { background:$surface; color:$accent; border-color:$accent; }
.badge-blue  { background:$surface; color:$technical; border-color:$technical; }
.badge-amber { background:$surface; color:$text_muted; }

div[data-testid="stChatMessage"] {
    background:transparent; border:none; border-radius:0;
    border-left:4px solid $border;
    padding:12px 0 12px 20px; margin-bottom:16px;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]),
div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    border-left-color:$text_muted;
}
div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"],
div[data-testid="chatAvatarIcon-user"], div[data-testid="chatAvatarIcon-assistant"] {
    display:none !important;
}

.source-card { background:$surface; border:1px solid $border; border-radius:4px; padding:14px; margin-bottom:8px; }
.source-card-title { font-size:0.8rem; font-weight:700; color:$text; margin-bottom:6px; }
.source-card-snippet { font-size:0.8rem; color:$text_muted; line-height:1.6; }
.source-card-rank { font-size:0.7rem; font-weight:600; color:$technical; margin-left:8px; }

.stExpander { border:none !important; border-radius:0 !important; background:transparent !important; margin-top:0 !important; box-shadow:none !important; }
section[data-testid="stSidebar"] .stExpander { border-bottom:1px solid $border !important; }
.stExpander summary { font-weight:600 !important; color:$text !important; font-size:0.85rem !important; padding:12px 2px !important; }
.stExpander summary:hover { color:$text !important; }
[data-testid="stExpanderDetails"] { padding-top:4px !important; }

.metric-strip { display:flex; align-items:stretch; background:$surface; border:1px solid $border; border-radius:4px; padding:8px 4px; margin-bottom:16px; }
.metric-item { flex:1; text-align:center; padding:4px 8px; }
.metric-item-val { display:block; font-size:1rem; font-weight:700; color:$text; line-height:1.3; }
.metric-item-lbl { display:block; font-size:0.65rem; color:$text_muted; text-transform:uppercase; letter-spacing:0.5px; margin-top:2px; }
.metric-divider { width:1px; align-self:stretch; background:$border; margin:4px 0; }

.arch-step { display:flex; align-items:flex-start; gap:16px; padding:12px 0; border-bottom:1px solid $border; }
.arch-step:last-child { border-bottom:none; }
.arch-num { min-width:28px; height:28px; background:$surface; border:1px solid $border; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:0.8rem; font-weight:700; color:$text; }
.arch-content { font-size:0.85rem; color:$text_muted; line-height:1.6; }
.arch-content b { color:$text; }
.arch-why { font-size:0.8rem; color:$text_dim; line-height:1.6; margin-top:8px; padding-left:12px; border-left:2px solid $border; }

.eval-summary-row { display:flex; gap:16px; margin:16px 0 24px 0; flex-wrap:wrap; }
.eval-stat { flex:1; min-width:140px; background:$surface; border:1px solid $border; border-radius:4px; padding:16px; text-align:center; }
.eval-stat-val { font-size:1.6rem; font-weight:700; color:$text; }
.eval-stat-lbl { font-size:0.7rem; color:$text_muted; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
.eval-row { display:flex; align-items:flex-start; gap:12px; background:$surface; border:1px solid $border; border-radius:4px; padding:14px; margin-bottom:8px; }
.eval-tag { font-size:0.7rem; font-weight:700; border-radius:2px; padding:4px 8px; white-space:nowrap; border:1px solid transparent; }
.eval-tag-correct { background:$surface_alt; color:$accent; border-color:$accent; }
.eval-tag-partial { background:$surface_alt; color:$technical; border-color:$technical; }
.eval-tag-declined { background:$surface_alt; color:$text_muted; border-color:$text_muted; }
.eval-q { font-size:0.85rem; color:$text; font-weight:600; }
.eval-note { font-size:0.8rem; color:$text_muted; margin-top:4px; }

.upload-card {
    background: $surface !important;
    border: 1px solid $border !important;
    border-radius: 4px !important;
    padding: 16px !important;
    text-align: center;
    margin: 8px 0;
}
/* File uploader */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploader"] > div,
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"],
div[data-testid="stFileUploaderDropzone"] {
    background: $surface !important;
    background-color: $surface !important;
    border: 1px dashed $text_dim !important;
    border-radius: 4px !important;
    color: $text_muted !important;
}
div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
    background: $surface_alt !important;
    background-color: $surface_alt !important;
    color: $text !important;
    border: 1px solid $border !important;
}
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] span {
    color: $text_muted !important;
}
.upload-title { font-weight:700; color:$text; font-size:0.85rem; }
.upload-sub { font-size:0.7rem; color:$text_dim; margin-top:4px; }

.pipeline-chip-row { display:flex; align-items:center; flex-wrap:wrap; gap:6px; margin:12px 0; }
.pipeline-chip { background:$surface; border:1px solid $border; border-radius:4px; padding:6px 12px; font-size:0.75rem; color:$text; font-weight:600; }
.pipeline-arrow { color:$text_dim; font-size:0.8rem; }
.pipeline-row {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: center;
    align-items: stretch;
    gap: 8px;
    margin-bottom: 24px;
}
.pipeline-node {
    flex: 0 0 auto;
    width: auto;
    min-width: 120px;
    background:$surface;
    border:1px solid $border;
    border-radius:4px;
    padding:16px;
    text-align:center;
}
.pipeline-node-icon { font-size:1.2rem; margin-bottom:8px; color:$technical; }
.pipeline-node-label { font-size:0.75rem; font-weight:700; color:$text; text-transform:uppercase; letter-spacing:0.5px; }
.pipeline-connector { display:flex; align-items:center; color:$text_dim; font-size:1.2rem; padding:0 4px; }
.suggested-label { font-size:0.8rem; font-weight:700; color:$text_muted; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px; text-align:left; }

/* RAG comparison cards */
.compare-card { background:$surface; border:1px solid $border; border-radius:4px; padding:16px; margin-bottom:8px; }
.compare-card-rag { border-top:2px solid $accent; }
.compare-card-direct { border-top:2px solid $text_muted; }
.compare-card-label { font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px; }
.compare-card-label-rag { color:$accent; }
.compare-card-label-direct { color:$text_muted; }
.compare-warning { background:$surface; border:1px solid $border; border-radius:4px; padding:12px 16px; font-size:0.8rem; color:$text_muted; margin-top:8px; }

/* Feedback row */
.feedback-row { display:flex; align-items:center; gap:12px; margin-top:12px; padding-top:12px; border-top:1px solid $border; }
.feedback-label { font-size:0.75rem; color:$text_dim; font-weight:600; }

@media (max-width: 768px) {
    .top-bar-title { font-size:1.2rem; }
    .pipeline-row { flex-direction: column !important; align-items: center; flex-wrap: wrap !important; }
    .pipeline-connector { transform: rotate(90deg); }
}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0rem !important;
}
.stApp > header {
    background-color: transparent !important;
}
footer, [data-testid="stFooter"] {
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
}

/* ===== FORCE REMOVE BOTTOM BLACK BAR ===== */
[data-testid="stBottom"],
div[data-testid="stChatInputContainer"],
.stChatFloatingInputContainer,
section[data-testid="stChatInput"],
.stApp > div:last-child,
div[data-testid="stBottomBlockContainer"],
[data-testid="stDecoration"] {
    background: transparent !important;
    background-color: transparent !important;
    border-top: none !important;
    box-shadow: none !important;
}
.stApp [data-testid="stBottom"] > div,
.stApp [data-testid="stChatInputContainer"] > div {
    background: transparent !important;
    background-color: transparent !important;
}

/* Chat input card */
div[data-testid="stChatInput"],
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] > div > div {
    background: $surface !important;
    background-color: $surface !important;
    border-color: $border !important;
    border-radius: 4px !important;
    color: $text !important;
}
div[data-testid="stChatInput"] textarea,
div[data-testid="stChatInput"] input,
div[data-testid="stChatInput"] [contenteditable="true"] {
    color: $text !important;
    background: transparent !important;
    caret-color: $text !important;
}
div[data-testid="stChatInput"] textarea::placeholder,
div[data-testid="stChatInput"] input::placeholder {
    color: $text_dim !important;
    opacity: 1 !important;
}

/* Full width when sidebar is collapsed */
section[data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container,
section[data-testid="stSidebar"][aria-expanded="false"] + .main .block-container,
div[data-testid="stAppViewContainer"] > .main .block-container {
    max-width: 100% !important;
}
.main .block-container {
    max-width: 1100px;
    margin: 0 auto;
    transition: max-width 0.25s ease;
}
[data-testid="stAppViewContainer"] .main {
    width: 100% !important;
}

/* Sidebar collapse / expand control */
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: $surface !important;
    border: 1px solid $border !important;
    border-radius: 4px !important;
    color: $text !important;
    z-index: 999999 !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] path {
    fill: $text !important;
    stroke: $text !important;
}
/* Collapse arrow on the open sidebar */
section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"],
section[data-testid="stSidebar"] button[kind="headerNoPadding"] {
    color: $text !important;
    background: $surface_alt !important;
    border: 1px solid $border !important;
    opacity: 1 !important;
    visibility: visible !important;
}

""")

def get_css(theme_name: str) -> str:
    T = THEMES[theme_name]
    _css = CSS_TEMPLATE.substitute(**T)
    return _css
