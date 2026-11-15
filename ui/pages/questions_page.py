import streamlit as st

def render_questions_page(T: dict):
    """
    Renders the approved Stitch Question Library screen (Screen ID: 4bb3df8be1684d0a9d971212bde085c1).
    Organizes solar questions by category with working 'Ask SolarSense' routing to Chat Assistant.
    """
    st.markdown("""
<div class="stitch-page-wrap">
    <div style="background:rgba(8,127,91,0.08);border:1px solid rgba(32,201,151,0.25);border-radius:10px;padding:4px 12px;display:inline-flex;align-items:center;gap:6px;font-size:0.75rem;font-weight:700;color:#087F5B;margin-bottom:10px;">
        <span>💡</span> DOMAIN VERIFIED QUESTION BANK &bull; 20 Curated Prompts
    </div>
    <div class="stitch-page-title-row">
        <div>
            <h1 class="stitch-page-title">Solar Knowledge Question Library</h1>
            <p class="stitch-page-desc">
                Explore curated, domain-verified rooftop solar questions organized by category for fast interaction with the SolarSense RAG assistant. Benchmark accuracy against statutory regulatory standards, Discom net metering acts, and real-time subsidy slabs.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Search filter
    search_query = st.text_input("🔍 Search question library by keyword (e.g. 'subsidy', 'tariff', 'battery', 'inverter')...", key="lib_search_input")

    QUESTION_DATA = [
        {
            "category_name": "PM Surya Ghar: Muft Bijli Yojana",
            "category_desc": "National scheme guidelines, eligibility criteria, and portal procedures",
            "tag_color": "#087F5B",
            "questions": [
                {
                    "title": "What is the PM Surya Ghar scheme and who is eligible?",
                    "tag": "Scheme Basics",
                    "doc": "02_pm_surya_ghar.txt",
                    "desc": "Inquire about consumer eligibility, residential rooftop space requirements, Discom consumer account rules, and sanctioned load limits.",
                    "query": "What is the PM Surya Ghar scheme and who is eligible?"
                },
                {
                    "title": "What is the maximum central subsidy under PM Surya Ghar?",
                    "tag": "Financial Subsidy",
                    "doc": "02_pm_surya_ghar.txt",
                    "desc": "Targeted ₹30,000/kW assistance up to 2kW, incremental ₹18,000 for the 3rd kW, capping at an official maximum central subsidy of ₹78,000.",
                    "query": "What is the subsidy under PM Surya Ghar?"
                },
                {
                    "title": "Is a special rooftop solar meter mandatory for PM Surya Ghar?",
                    "tag": "Technical Hardware",
                    "doc": "03_technical_faq.txt",
                    "desc": "Central Electricity Authority (CEA) specifications for bidirectional metering, generation meters vs. import/export meters, and Discom procurement rules.",
                    "query": "Is a bidirectional net meter mandatory for PM Surya Ghar rooftop solar?"
                },
            ]
        },
        {
            "category_name": "Subsidy, Economics & Return on Investment",
            "category_desc": "Capital outlays, payback horizon benchmarks, and state vs. central top-up incentives",
            "tag_color": "#D97706",
            "questions": [
                {
                    "title": "How is the subsidy calculated for systems larger than 3 kW?",
                    "tag": "Calculation & Ceilings",
                    "doc": "02_pm_surya_ghar.txt",
                    "desc": "Clarifies whether systems exceeding 3kW (e.g., 5kW or 10kW) continue to receive incremental financial assistance or remain restricted to the ₹78,000 threshold.",
                    "query": "How is the subsidy calculated for systems larger than 3 kW under PM Surya Ghar?"
                },
                {
                    "title": "What is the typical payback period for a 3kW residential rooftop system in India?",
                    "tag": "Payback & ROI",
                    "doc": "02_pm_surya_ghar.txt",
                    "desc": "Evaluates ₹1.65L net capital outlay after subsidies (~₹1.2L–₹1.5L) against monthly power bill offsets at an average of ₹7.5–₹9/kWh (3.0 to 4.2 year payback).",
                    "query": "What is the payback period for a 3kW or 5kW system?"
                },
                {
                    "title": "What is the dust-loss penalty and how does it impact generation savings?",
                    "tag": "Performance Loss",
                    "doc": "03_technical_faq.txt",
                    "desc": "Analysis of soiling losses, dust accumulation penalties on panel efficiency, and recommended cleaning frequencies to protect annual solar returns.",
                    "query": "What is dust-loss penalty and how does it affect solar panel efficiency?"
                },
            ]
        },
        {
            "category_name": "Net Metering, Discoms & Regulations",
            "category_desc": "Grid synchronization, billing settlement cycles, and mandatory utility clearances",
            "tag_color": "#20C997",
            "questions": [
                {
                    "title": "How does net metering work versus gross metering?",
                    "tag": "Metering Types",
                    "doc": "01_dispatch_modes.txt",
                    "desc": "Contrasts offsetting self-consumed electricity at retail power rates (net metering) against selling 100% of generated solar units at predetermined feed-in tariffs (gross metering).",
                    "query": "How does net metering work versus gross metering?"
                },
                {
                    "title": "What happens to excess electricity generated by my solar panels at settlement?",
                    "tag": "Banking & Settlement",
                    "doc": "01_dispatch_modes.txt",
                    "desc": "Explains monthly banking credit carryover, fiscal year-end true-up (typically March 31), and APPC (Average Power Purchase Cost) cash payouts or lapse rules.",
                    "query": "What happens to excess solar electricity at the end of the settlement period?"
                },
                {
                    "title": "Do I need Discom approval or NOC before installing rooftop solar?",
                    "tag": "Utility Approvals",
                    "doc": "00_system_overview.txt",
                    "desc": "Details technical feasibility approval (TFA) processes, sanctioned load limits (typically 80% to 100% of consumer sanctioned load), and distribution transformer capacity limits.",
                    "query": "Do I need Discom approval or NOC before installing rooftop solar?"
                },
            ]
        },
        {
            "category_name": "Battery Storage, Inverters & Sizing",
            "category_desc": "LiFePO4 BESS sizing, hybrid vs. on-grid inverters, and black-start resilience",
            "tag_color": "#052E24",
            "questions": [
                {
                    "title": "What size battery do I need for backup during power outages with a 3kW system?",
                    "tag": "Storage Engineering",
                    "doc": "03_technical_faq.txt",
                    "desc": "Walks through critical load runtime configuration (lights, fans, essential routers continuous), Depth of Discharge (DoD 80% for LFP), calculating between 3kWh to 10kWh capacity.",
                    "query": "How is the battery sized for a 3kW system?"
                },
                {
                    "title": "Explain Backup Priority mode versus Cost-Save mode in hybrid systems",
                    "tag": "Inverter Architectures",
                    "doc": "01_dispatch_modes.txt",
                    "desc": "Comprehensive comparison between maintaining full battery state of charge for unexpected outages versus cycling stored energy during peak tariff hours.",
                    "query": "Compare Cost-Save and Backup Priority mode"
                },
                {
                    "title": "How does monsoon pre-charge work for battery systems?",
                    "tag": "Smart Automation",
                    "doc": "01_dispatch_modes.txt",
                    "desc": "Details smart inverter logic that triggers grid-connected top-up charging prior to forecasted heavy cloud cover or cyclonic weather alerts.",
                    "query": "How does monsoon pre-charge work?"
                },
            ]
        }
    ]

    # Render Categories & Cards
    for cat_idx, cat in enumerate(QUESTION_DATA):
        matching_q = [
            q for q in cat["questions"]
            if not search_query or search_query.lower() in q["title"].lower() or search_query.lower() in q["desc"].lower()
        ]
        if not matching_q:
            continue

        st.markdown(f"""
<div style="margin-top:24px;margin-bottom:14px;">
    <div style="display:flex;align-items:center;gap:8px;">
        <span style="font-size:1rem;color:{cat['tag_color']};">●</span>
        <h3 style="font-size:1.15rem;font-weight:700;color:{T['text']};margin:0;">{cat['category_name']}</h3>
    </div>
    <div style="font-size:0.78rem;color:{T['text_muted']};margin-top:2px;margin-left:18px;">{cat['category_desc']}</div>
</div>
""", unsafe_allow_html=True)

        cols = st.columns(len(matching_q) if len(matching_q) <= 3 else 3, gap="medium")
        for q_idx, q in enumerate(matching_q):
            col = cols[q_idx % 3]
            with col:
                st.markdown(f"""
<div class="stitch-qcard">
    <div>
        <span class="stitch-qcard-tag" style="background:{T['surface_alt']};color:{cat['tag_color']};border:1px solid {T['border']};">
            {q['tag']} &bull; {q['doc']}
        </span>
        <div class="stitch-qcard-title">"{q['title']}"</div>
        <div class="stitch-qcard-desc">{q['desc']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

                btn_key = f"q_btn_{cat_idx}_{q_idx}"
                if st.button("💬 Ask SolarSense ➔", key=btn_key, type="primary", use_container_width=True):
                    st.session_state["pending_prompt"] = q["query"]
                    st.session_state.current_page = "Chat Assistant"
                    st.rerun()
