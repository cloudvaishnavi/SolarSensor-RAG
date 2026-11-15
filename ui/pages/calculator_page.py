import os
import streamlit as st
from backend.text_utils import img_to_b64

def render_calculator_page(T: dict):
    """
    Renders the approved Stitch PM Surya Ghar Solar Calculator screen (Screen ID: 842bbb2204c54588b2b11511466a2722).
    Uses the official MNRE PM Surya Ghar formula and benchmark assumptions.
    """
    st.markdown("""
<div class="stitch-page-wrap">
    <div style="background:rgba(8,127,91,0.08);border:1px solid rgba(32,201,151,0.25);border-radius:10px;padding:8px 14px;display:inline-flex;align-items:center;gap:8px;font-size:0.75rem;font-weight:700;color:#087F5B;margin-bottom:10px;">
        <span>ℹ️</span> OFFICIAL BENCHMARK FRAMEWORK &bull; MNRE 2024-25
    </div>
    <div class="stitch-page-title-row">
        <div>
            <h1 class="stitch-page-title">PM Surya Ghar Solar Calculator</h1>
            <p class="stitch-page-desc">
                Estimate recommended rooftop solar system capacity, central subsidy under PM Surya Ghar: Muft Bijli Yojana, and projected bill savings based on current guidelines.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ----------------------------------------------------------------
    # 2-Column Responsive Layout: Inputs on Left, Results on Right
    # ----------------------------------------------------------------
    left_col, right_col = st.columns([45, 55], gap="large")

    with left_col:
        with st.container(key="calc_inputs_card"):
            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
    <h3 class="stitch-card-title" style="margin-bottom:0;">System Inputs</h3>
    <span style="font-size:0.72rem;color:{T['text_dim']};">Domestic Residential</span>
</div>
""", unsafe_allow_html=True)

        monthly_bill = st.slider(
            "Average Monthly Electricity Bill (₹)",
            min_value=800,
            max_value=15000,
            value=3500,
            step=250,
            key="calc_bill_slider",
            help="Your average monthly power bill from Discom before solar installation."
        )

        est_tariff = 8.0  # ~Rs 8 per unit average domestic slab
        monthly_units = int(monthly_bill / est_tariff)
        calc_kw = round(monthly_units / (4.0 * 30), 1)  # 4 units per kWp per day
        calc_kw = max(1.0, min(10.0, calc_kw))

        st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0 16px 0;">
    <div style="background:{T['surface_alt']};border:1px solid {T['border']};border-radius:10px;padding:12px;">
        <div style="font-size:0.72rem;color:{T['text_muted']};font-weight:700;">MONTHLY UNITS (kWh)</div>
        <div style="font-size:1.25rem;font-weight:800;color:{T['text']};margin-top:2px;">~{monthly_units} <span style="font-size:0.75rem;font-weight:500;">kWh</span></div>
        <div style="font-size:0.68rem;color:{T['text_dim']};margin-top:2px;">Derived from ~₹8/unit slab</div>
    </div>
    <div style="background:{T['surface_alt']};border:1px solid {T['border']};border-radius:10px;padding:12px;">
        <div style="font-size:0.72rem;color:{T['text_muted']};font-weight:700;">SHADE-FREE ROOF AREA</div>
        <div style="font-size:1.25rem;font-weight:800;color:{T['text']};margin-top:2px;">~{int(calc_kw * 100)} <span style="font-size:0.75rem;font-weight:500;">sq. ft</span></div>
        <div style="font-size:0.68rem;color:{T['text_dim']};margin-top:2px;">~100 sq.ft per kWp required</div>
    </div>
</div>
""", unsafe_allow_html=True)

        system_kw = st.number_input(
            "Selected System Size (kWp)",
            min_value=1.0,
            max_value=10.0,
            value=float(calc_kw),
            step=0.5,
            key="calc_system_kw_input",
            help="Adjust capacity manually if you desire higher generation or have specific roof limits."
        )

        discom = st.selectbox(
            "State & Electricity Utility (Discom)",
            options=[
                "Maharashtra — MSEDCL (Mahavitaran)",
                "Delhi — BSES Rajdhani / Yamuna (BRPL/BYPL)",
                "Gujarat — DGVCL / MGVCL / PGVCL",
                "Karnataka — BESCOM",
                "Tamil Nadu — TANGEDCO",
                "Uttar Pradesh — UPPCL",
                "Other / National Net Metering Framework"
            ],
            key="calc_discom_select"
        )

        grid_phase = st.radio(
            "Grid Connection Class",
            ["Residential 1-Phase (Up to 3-5 kW)", "Residential 3-Phase (Over 5 kW)"],
            index=0,
            key="calc_grid_phase"
        )

        include_battery = st.checkbox(
            "Include Battery Storage (BESS) for grid power outage backup (Hybrid System)",
            value=False,
            key="calc_battery_checkbox"
        )

    with right_col:
        # MNRE PM Surya Ghar Official Subsidy Calculation
        if system_kw <= 2.0:
            subsidy = 30_000 * system_kw
            is_capped = False
            first_kw_sub = min(system_kw, 1.0) * 30_000
            second_kw_sub = max(0.0, system_kw - 1.0) * 30_000
            third_kw_sub = 0
        elif system_kw <= 3.0:
            subsidy = 60_000 + (system_kw - 2.0) * 18_000
            is_capped = (system_kw >= 3.0)
            first_kw_sub = 30_000
            second_kw_sub = 30_000
            third_kw_sub = (system_kw - 2.0) * 18_000
        else:
            subsidy = 78_000
            is_capped = True
            first_kw_sub = 30_000
            second_kw_sub = 30_000
            third_kw_sub = 18_000

        turnkey_cost = system_kw * 55_000
        if include_battery:
            turnkey_cost += 70_000  # ~5 kWh LiFePO4 battery pack
        net_customer_outflow = max(0.0, turnkey_cost - subsidy)
        annual_units = system_kw * 1400  # ~1400 units/kW/year
        annual_savings = annual_units * 7.5
        payback_years = net_customer_outflow / annual_savings if annual_savings > 0 else 0

        # Optimal Sizing & Central Subsidy Grid
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            st.markdown(f"""
<div class="stitch-optimal-card">
    <div style="font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#A3E635;">OPTIMAL SIZING</div>
    <div class="stitch-optimal-kw">{system_kw:.1f} <span style="font-size:1.2rem;font-weight:500;">kW System</span></div>
    <div style="font-size:0.78rem;color:#E2ECE7;line-height:1.4;">
        Engineered to offset 100% of your ~{monthly_units} units monthly demand.
    </div>
    <div style="margin-top:12px;font-size:0.75rem;color:#F4F8F2;border-top:1px solid rgba(255,255,255,0.2);padding-top:8px;">
        Roof Needed: <b>~{int(system_kw * 100)} sq. ft</b>
    </div>
</div>
""", unsafe_allow_html=True)

        with s_col2:
            st.markdown(f"""
<div class="stitch-card" style="margin-bottom:16px;">
    <div style="display:flex;align-items:center;justify-content:space-between;">
        <span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;color:{T['text_muted']};">DIRECT CENTRAL SUBSIDY</span>
        <span style="font-size:0.68rem;font-weight:700;background:rgba(8,127,91,0.12);color:#087F5B;padding:2px 8px;border-radius:9999px;">DBT Approved</span>
    </div>
    <div style="font-size:2rem;font-weight:800;color:{T['text']};margin:6px 0;">₹{subsidy:,.0f}</div>
    <div style="font-size:0.74rem;line-height:1.6;color:{T['text_muted']};">
        1st kW Central Grant: <b>₹{first_kw_sub:,.0f}</b><br>
        2nd kW Central Grant: <b>₹{second_kw_sub:,.0f}</b><br>
        3rd kW Central Grant: <b>₹{third_kw_sub:,.0f}</b><br>
        {"<span style='color:#087F5B;font-weight:700;'>● Maximum ₹78,000 Cap Reached</span>" if is_capped else ""}
    </div>
</div>
""", unsafe_allow_html=True)

        # Financial Outflow & Payback Card
        calc_card_html = (
            f'<div class="stitch-card">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">'
            f'<h4 style="font-size:0.95rem;font-weight:700;color:{T["text"]};margin:0;">Financial Outflow & Payback</h4>'
            f'<span style="font-size:0.7rem;color:{T["text_dim"]};">MNRE Benchmark 2024</span>'
            f'</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:16px;">'
            f'<div style="background:{T["surface_alt"]};border:1px solid {T["border"]};border-radius:10px;padding:12px;">'
            f'<div style="font-size:0.68rem;font-weight:700;color:{T["text_muted"]};">BENCHMARK COST</div>'
            f'<div style="font-size:1.15rem;font-weight:800;color:{T["text"]};margin-top:2px;">₹{turnkey_cost:,.0f}</div>'
            f'<div style="font-size:0.68rem;color:{T["text_dim"]};">{"Incl. Battery BESS" if include_battery else "Tier-1 DCR Panels"}</div>'
            f'</div>'
            f'<div style="background:{T["surface_alt"]};border:1px solid {T["border"]};border-radius:10px;padding:12px;">'
            f'<div style="font-size:0.68rem;font-weight:700;color:{T["text_muted"]};">LESS SUBSIDY</div>'
            f'<div style="font-size:1.15rem;font-weight:800;color:#087F5B;margin-top:2px;">-₹{subsidy:,.0f}</div>'
            f'<div style="font-size:0.68rem;color:{T["text_dim"]};">Direct DBT transfer</div>'
            f'</div>'
            f'<div style="background:{T["surface_subtle"]};border:1px solid {T["border"]};border-radius:10px;padding:12px;">'
            f'<div style="font-size:0.68rem;font-weight:700;color:#052E24;">NET OUTFLOW</div>'
            f'<div style="font-size:1.15rem;font-weight:800;color:#087F5B;margin-top:2px;">₹{net_customer_outflow:,.0f}</div>'
            f'<div style="font-size:0.68rem;color:#64756B;">Total investment</div>'
            f'</div>'
            f'</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">'
            f'<div style="padding:10px;background:{T["surface_alt"]};border-radius:8px;font-size:0.78rem;"><b>Est. Annual Generation:</b> {annual_units:,.0f} kWh / yr</div>'
            f'<div style="padding:10px;background:{T["surface_alt"]};border-radius:8px;font-size:0.78rem;"><b>Est. Annual Savings:</b> ₹{annual_savings:,.0f} / yr</div>'
            f'</div>'
            f'<div style="background:{T["surface_subtle"]};border-radius:10px;padding:12px;display:flex;align-items:center;justify-content:space-between;">'
            f'<div><div style="font-size:0.75rem;font-weight:700;color:{T["text"]};">Projected Payback Horizon</div>'
            f'<div style="font-size:0.7rem;color:{T["text_muted"]};">Capital recovery through electricity offset</div></div>'
            f'<div style="font-size:1.35rem;font-weight:800;color:#087F5B;">~{payback_years:.1f} <span style="font-size:0.8rem;font-weight:600;">Years</span></div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(calc_card_html, unsafe_allow_html=True)

        # Working Action Button that routes to Chat Assistant
        calc_q = f"Under PM Surya Ghar, what are the details for a {system_kw:.1f}kW rooftop solar system with ₹{subsidy:,.0f} subsidy for {discom}?"
        if st.button("💬 Ask SolarSense AI About These Sizing Results ➔", type="primary", use_container_width=True, key="calc_ask_ai_btn"):
            st.session_state["pending_prompt"] = calc_q
            st.session_state.current_page = "Chat Assistant"
            st.rerun()

    # ----------------------------------------------------------------
    # Bottom Photographic Gallery (Architectural Assets from Stitch)
    # ----------------------------------------------------------------
    img1_path = "assets/solar_calc_img_1.png"
    img2_path = "assets/solar_calc_img_2.png"
    img1_b64 = img_to_b64(img1_path) if os.path.exists(img1_path) else ""
    img2_b64 = img_to_b64(img2_path) if os.path.exists(img2_path) else ""

    if img1_b64 and img2_b64:
        st.markdown(f"""
<div style="margin-top:20px;display:grid;grid-template-columns:1fr 1fr 1.2fr;gap:14px;">
    <div style="position:relative;border-radius:14px;overflow:hidden;border:1px solid {T['border']};height:170px;">
        <img src="data:image/png;base64,{img1_b64}" style="width:100%;height:100%;object-fit:cover;" alt="Solar Panels on Roof"/>
        <div style="position:absolute;bottom:0;inset-x:0;background:linear-gradient(transparent, rgba(0,0,0,0.75));padding:10px 12px;color:#FFFFFF;">
            <div style="font-size:0.68rem;text-transform:uppercase;color:#A3E635;font-weight:700;">Standard Rooftop Model</div>
            <div style="font-size:0.82rem;font-weight:700;">Standard Elevated MMS Mounting</div>
        </div>
    </div>
    <div style="position:relative;border-radius:14px;overflow:hidden;border:1px solid {T['border']};height:170px;">
        <img src="data:image/png;base64,{img2_b64}" style="width:100%;height:100%;object-fit:cover;" alt="Net Metering and Inverter"/>
        <div style="position:absolute;bottom:0;inset-x:0;background:linear-gradient(transparent, rgba(0,0,0,0.75));padding:10px 12px;color:#FFFFFF;">
            <div style="font-size:0.68rem;text-transform:uppercase;color:#A3E635;font-weight:700;">Net Metering Infrastructure</div>
            <div style="font-size:0.82rem;font-weight:700;">Smart Grid Synchronized Inverter</div>
        </div>
    </div>
    <div class="stitch-card" style="margin-bottom:0;display:flex;flex-direction:column;justify-content:center;height:170px;background:{T['surface_alt']};">
        <div style="display:flex;align-items:center;gap:6px;font-size:0.75rem;font-weight:700;color:{T['accent']};margin-bottom:6px;">
            <span>💡</span> SolarSense AI Engineering Guidance
        </div>
        <p style="font-size:0.78rem;color:{T['text_muted']};line-height:1.45;margin:0;">
            Based on your <b>₹{monthly_bill:,}</b> monthly bill, a <b>{system_kw:.1f} kW</b> system provides the highest ROI under the PM Surya Ghar subsidy structure, capturing <b>₹{subsidy:,.0f}</b> in direct central assistance.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
