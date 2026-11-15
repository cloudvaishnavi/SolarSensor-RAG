"""
SolarSense AI — Authentication Pages
Login, Sign Up, and Forgot Password presentation screens.
Consistent with the approved SolarSense grey-green design system.
Integrates with ui/auth_service.py for genuine Supabase Auth operations.
"""

import base64
import os
import textwrap
import streamlit as st

from ui.auth_service import (
    is_auth_configured,
    sign_in,
    sign_up,
    reset_password,
    is_valid_email,
    get_setup_instructions,
)


def _get_logo_b64() -> str:
    """Read local logo.jpg and return base64 string."""
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.jpg")
    if os.path.exists(logo_path):
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return ""
    return ""


def _render_html(html_str: str):
    """Safely render application-authored HTML using st.html with dedent."""
    clean = textwrap.dedent(html_str).strip()
    st.html(clean)


def _scoped_auth_css():
    """Apply styling for centered 480-540px auth card on grey-green canvas."""
    st.markdown(
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
            max-width: 520px !important;
            margin: 0 auto !important;
            padding-top: 2.5rem !important;
            padding-bottom: 3.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        div[data-testid="stForm"] {
            background: #FFFFFF !important;
            border: 1.5px solid #C9DCCF !important;
            border-radius: 18px !important;
            padding: 28px !important;
            box-shadow: 0 4px 18px rgba(8, 127, 91, 0.08) !important;
        }
        div.st-key-auth_card_container {
            max-width: 520px !important;
            margin: 0 auto !important;
        }
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
        """,
        unsafe_allow_html=True,
    )


def _navigate_to(page: str):
    """Safely navigate to a target page, keeping session state and query params synchronized."""
    st.session_state["current_page"] = page
    st.session_state["_last_query_page"] = page
    st.query_params["page"] = page
    st.rerun()


def _render_logo_header(title: str, subtitle: str):
    """Render consistent header with actual logo image asset."""
    logo_b64 = _get_logo_b64()
    if logo_b64:
        logo_markup = f'<img src="data:image/jpeg;base64,{logo_b64}" alt="SolarSense Logo" style="width:38px;height:38px;border-radius:10px;object-fit:cover;box-shadow:0 2px 6px rgba(8,127,91,0.25);"/>'
    else:
        logo_markup = '<div style="width:38px;height:38px;border-radius:10px;background:#087F5B;color:#A3E635;display:flex;align-items:center;justify-content:center;font-size:1.3rem;font-weight:800;box-shadow:0 2px 6px rgba(8,127,91,0.25);">☀️</div>'

    _render_html(
        f"""
        <div style="background:#FFFFFF; border:1.5px solid #C9DCCF; border-radius:20px; padding:32px 28px; box-shadow:0 8px 26px -6px rgba(8,127,91,0.08); margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px;">
                {logo_markup}
                <div>
                    <div style="font-size:1.2rem; font-weight:800; color:#052E24; letter-spacing:-0.02em; line-height:1.1;">SolarSense AI</div>
                    <div style="font-size:0.74rem; font-weight:600; color:#64756B;">Clean Energy Intelligence</div>
                </div>
            </div>
            <h1 style="font-size:1.75rem; font-weight:800; color:#052E24; margin:0 0 8px 0; letter-spacing:-0.02em; line-height:1.25;">{title}</h1>
            <p style="font-size:0.86rem; color:#64756B; margin:0; line-height:1.55;">
                {subtitle}
            </p>
        </div>
        """
    )


def render_login_page(T: dict):
    """Renders the centered, refined Login screen."""
    _scoped_auth_css()
    _, col_center, _ = st.columns([1, 1.35, 1])
    with col_center:
        _render_logo_header(
            title="Sign in to your SolarSense workspace",
            subtitle="Continue exploring rooftop solar knowledge, scheme guidance, and your saved solar conversations.",
        )

        configured = is_auth_configured()

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email address", placeholder="name@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pwd")
            login_submitted = st.form_submit_button("Log In →", type="primary", use_container_width=True)

        if login_submitted:
            if not email or not email.strip():
                st.error("Please enter your email address.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address (e.g. name@example.com).")
            elif not password:
                st.error("Please enter your password.")
            else:
                if configured:
                    with st.spinner("Signing in with Supabase Auth…"):
                        res = sign_in(email, password)
                    if res["success"]:
                        st.success("Authentication successful! Loading workspace…")
                        _navigate_to("Chat Assistant")
                    else:
                        st.error(res["error"])
                else:
                    st.info(
                        """
                        ℹ️ **Authentication Provider Notice**  
                        Supabase authentication is not yet configured for this instance.  
                        To enable genuine account logins, add your Supabase URL and anon key to `.streamlit/secrets.toml`.
                        """
                    )
                    if st.button("Enter Dashboard in Preview Mode ➔", key="login_preview_btn", type="primary", use_container_width=True):
                        st.session_state["authenticated"] = True
                        st.session_state["preview_mode"] = True
                        st.session_state["user_name"] = "Preview Visitor"
                        _navigate_to("Chat Assistant")

        # Helpful guide if not configured
        if not configured and not login_submitted:
            with st.expander("🛠️ How to connect Supabase Authentication", expanded=False):
                st.markdown(get_setup_instructions())
                if st.button("Explore Dashboard in Preview Mode ↗", key="login_unconf_preview_btn", use_container_width=True):
                    st.session_state["authenticated"] = True
                    st.session_state["preview_mode"] = True
                    st.session_state["user_name"] = "Preview Visitor"
                    _navigate_to("Chat Assistant")

        # Navigation links underneath form
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            if st.button("Forgot Password?", key="login_to_forgot", use_container_width=True):
                _navigate_to("forgot_password")
        with link_col2:
            if st.button("Create an account", key="login_to_signup", use_container_width=True):
                _navigate_to("signup")

        _render_html("<div style='height:10px;'></div>")
        if st.button("← Back to SolarSense Home", key="login_to_home", use_container_width=True):
            _navigate_to("landing")


def render_signup_page(T: dict):
    """Renders the centered, refined Sign Up screen."""
    _scoped_auth_css()
    _, col_center, _ = st.columns([1, 1.35, 1])
    with col_center:
        _render_logo_header(
            title="Create Your SolarSense Account",
            subtitle="Sign up to access verified PM Surya Ghar guidance, rooftop sizing calculators, and AI document search.",
        )

        configured = is_auth_configured()

        with st.form("signup_form", clear_on_submit=False):
            full_name = st.text_input("Full name", placeholder="e.g. Ramesh Sharma", key="signup_name")
            email = st.text_input("Email address", placeholder="name@example.com", key="signup_email")
            password = st.text_input("Password (min 6 characters)", type="password", placeholder="Create a secure password", key="signup_pwd")
            confirm_pwd = st.text_input("Confirm password", type="password", placeholder="Repeat password", key="signup_confirm_pwd")

            terms = st.checkbox("I agree to the SolarSense Terms of Service and Privacy Policy", key="signup_terms")

            signup_submitted = st.form_submit_button("Create Account →", type="primary", use_container_width=True)

        if signup_submitted:
            if not full_name or not full_name.strip():
                st.error("Please enter your full name.")
            elif not email or not email.strip():
                st.error("Please enter your email address.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            elif not password or len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            elif password != confirm_pwd:
                st.error("Passwords do not match. Please re-enter your password.")
            elif not terms:
                st.error("Please accept the Terms of Service to continue.")
            else:
                if configured:
                    with st.spinner("Creating account with Supabase Auth…"):
                        res = sign_up(email, password, full_name)
                    if res["success"]:
                        if res.get("email_confirmation_required"):
                            st.success(
                                f"Account registered successfully! A confirmation link has been sent to **{email}**.\n\n"
                                "Please check your inbox and confirm your address before logging in."
                            )
                            if st.button("Proceed to Log In →", key="signup_success_to_login", type="primary", use_container_width=True):
                                _navigate_to("login")
                        else:
                            st.success("Account created and verified! Redirecting to workspace…")
                            st.session_state["authenticated"] = True
                            st.session_state["user_name"] = full_name
                            st.session_state["user_email"] = email
                            _navigate_to("Chat Assistant")
                    else:
                        st.error(res["error"])
                else:
                    st.info(
                        """
                        ℹ️ **Authentication Provider Notice**  
                        Supabase authentication is not yet configured for this instance.  
                        To persist user registrations across sessions, please configure Supabase credentials in `.streamlit/secrets.toml`.
                        """
                    )
                    if st.button("Enter Dashboard in Preview Mode ➔", key="signup_preview_btn", type="primary", use_container_width=True):
                        st.session_state["authenticated"] = True
                        st.session_state["preview_mode"] = True
                        st.session_state["user_name"] = full_name or "Preview Visitor"
                        _navigate_to("Chat Assistant")

        if not configured and not signup_submitted:
            with st.expander("🛠️ How to connect Supabase Authentication", expanded=False):
                st.markdown(get_setup_instructions())
                if st.button("Explore Dashboard in Preview Mode ↗", key="signup_unconf_preview_btn", use_container_width=True):
                    st.session_state["authenticated"] = True
                    st.session_state["preview_mode"] = True
                    st.session_state["user_name"] = "Preview Visitor"
                    _navigate_to("Chat Assistant")

        _render_html("<div style='height:8px;'></div>")
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            if st.button("Already have an account? Log In", key="signup_to_login", use_container_width=True):
                _navigate_to("login")
        with link_col2:
            if st.button("← Back to Home", key="signup_to_home", use_container_width=True):
                _navigate_to("landing")


def render_forgot_password_page(T: dict):
    """Renders the centered Forgot Password screen."""
    _scoped_auth_css()
    _, col_center, _ = st.columns([1, 1.35, 1])
    with col_center:
        _render_logo_header(
            title="Reset your password",
            subtitle="Enter the email address associated with your SolarSense account and we'll send you a password reset link.",
        )

        configured = is_auth_configured()

        with st.form("forgot_password_form", clear_on_submit=False):
            email = st.text_input("Registered email address", placeholder="name@example.com", key="forgot_email")
            reset_submitted = st.form_submit_button("Send Reset Link →", type="primary", use_container_width=True)

        if reset_submitted:
            if not email or not email.strip():
                st.error("Please enter your email address.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            else:
                if configured:
                    with st.spinner("Submitting password reset request…"):
                        res = reset_password(email)
                    if res["success"]:
                        st.success(
                            f"If an account is associated with **{email}**, password reset instructions have been sent. "
                            "Please check your inbox."
                        )
                    else:
                        st.error(res["error"])
                else:
                    st.info(
                        f"""
                        ℹ️ **Password Reset Notice**  
                        Reset token requested for `{email}`.  
                        An active Supabase Auth configuration with configured SMTP settings is required to deliver real password recovery emails.
                        """
                    )

        _render_html("<div style='height:8px;'></div>")
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            if st.button("← Back to Log In", key="forgot_to_login", use_container_width=True):
                _navigate_to("login")
        with link_col2:
            if st.button("← Back to Home", key="forgot_to_home", use_container_width=True):
                _navigate_to("landing")
