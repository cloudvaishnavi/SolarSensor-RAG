"""
SolarSense AI — Authentication Service
Isolated UI-level authentication service utilizing Supabase Auth.
Strictly separates authentication logic from the backend RAG pipeline.

Credentials are read safely from Streamlit secrets (`st.secrets["supabase"]`)
or environment variables (`SUPABASE_URL`, `SUPABASE_KEY`).
NEVER uses service_role secret keys.
"""

import os
import re
from typing import Dict, Any, Optional
import streamlit as st

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = Any


def _get_credentials() -> tuple[Optional[str], Optional[str]]:
    """Retrieve Supabase URL and Publishable Anon Key safely."""
    url = None
    key = None

    # 1. Try Streamlit Secrets
    # secrets.toml uses [supabase] section with keys: url, anon_key
    try:
        if hasattr(st, "secrets") and "supabase" in st.secrets:
            url = st.secrets["supabase"].get("url")
            # Accept both "anon_key" (secrets.toml convention) and legacy "key"
            key = st.secrets["supabase"].get("anon_key") or st.secrets["supabase"].get("key")
    except Exception:
        pass

    # 1b. Direct file fallback if st.secrets is unavailable or not yet mounted
    if not url or not key:
        try:
            secrets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".streamlit", "secrets.toml")
            if os.path.exists(secrets_path):
                import toml
                s = toml.load(secrets_path)
                sup = s.get("supabase", {})
                if not url:
                    url = sup.get("url")
                if not key:
                    key = sup.get("anon_key") or sup.get("key")
        except Exception:
            pass

    # 2. Fallback to Environment Variables
    if not url:
        url = os.environ.get("SUPABASE_URL")
    if not key:
        key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

    # Filter placeholder values
    if url and ("your-project-id" in url or "example.com" in url):
        url = None
    if key and ("your-anon" in key or "placeholder" in key):
        key = None

    return url, key


@st.cache_resource(show_spinner=False)
def _create_cached_client(url: str, key: str) -> Optional[Client]:
    """Helper to cache only valid client instances without permanently caching None."""
    try:
        return create_client(url, key)
    except Exception:
        return None


def get_auth_client() -> Optional[Client]:
    """Get or initialize cached Supabase client."""
    if not SUPABASE_AVAILABLE:
        return None

    url, key = _get_credentials()
    if not url or not key:
        return None

    return _create_cached_client(url, key)


def is_auth_configured() -> bool:
    """Return True if Supabase client is properly initialized with valid credentials."""
    url, key = _get_credentials()
    return bool(SUPABASE_AVAILABLE and url and key)


def get_setup_instructions() -> str:
    """Return clear instructions for configuring Supabase Auth."""
    return (
        "**Supabase Authentication Configuration Required**\n\n"
        "To enable real user registration and login:\n"
        "1. Create a project at [supabase.com](https://supabase.com).\n"
        "2. Copy your **Project URL** and **anon public API Key** from `Project Settings -> API`.\n"
        "3. Add them to `.streamlit/secrets.toml`:\n"
        "```toml\n"
        "[supabase]\n"
        "url = \"https://<your-project-id>.supabase.co\"\n"
        "key = \"<your-anon-publishable-key>\"\n"
        "```\n"
        "4. In Supabase Dashboard under `Authentication -> URL Configuration`, set Site URL to `http://localhost:8501`."
    )


def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, (email or "").strip()))


def sign_up(email: str, password: str, full_name: str = "") -> Dict[str, Any]:
    """
    Register a new user with Supabase Auth.
    Does not assume registration success merely because form validation passed.
    """
    if not is_auth_configured():
        return {
            "success": False,
            "error": "Authentication provider is not yet configured. Please add your Supabase credentials in .streamlit/secrets.toml.",
            "unconfigured": True,
        }

    client = get_auth_client()
    if not client:
        return {
            "success": False,
            "error": "Unable to connect to authentication client.",
            "unconfigured": True,
        }

    try:
        options = {}
        if full_name:
            options["data"] = {"full_name": full_name.strip()}

        res = client.auth.sign_up({
            "email": email.strip(),
            "password": password,
            "options": options,
        })

        user = res.user
        session = res.session

        # In Supabase GoTrue, if an account already exists and email confirmation is enabled,
        # it returns a User object with identities == [] to prevent email enumeration.
        if user and hasattr(user, "identities") and user.identities is not None and len(user.identities) == 0:
            return {
                "success": False,
                "error": "An account with this email address already exists. Please log in instead.",
                "unconfigured": False,
            }

        # In Supabase, if email confirmation is enabled, session might be None initially
        email_confirmation_required = session is None

        return {
            "success": True,
            "user": user,
            "session": session,
            "email_confirmation_required": email_confirmation_required,
            "error": None,
        }
    except Exception as e:
        err_msg = str(e)
        if "already registered" in err_msg.lower():
            err_msg = "An account with this email address already exists. Please log in instead."
        elif "password should be" in err_msg.lower():
            err_msg = "Password does not meet the provider's security requirements (minimum 6 characters)."
        return {
            "success": False,
            "error": err_msg,
            "unconfigured": False,
        }


def sign_in(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate an existing user with Supabase Auth.
    Sets session state only after genuine provider success.
    """
    if not is_auth_configured():
        return {
            "success": False,
            "error": "Authentication provider is not yet configured. Please add your Supabase credentials in .streamlit/secrets.toml.",
            "unconfigured": True,
        }

    client = get_auth_client()
    if not client:
        return {
            "success": False,
            "error": "Unable to connect to authentication client.",
            "unconfigured": True,
        }

    try:
        res = client.auth.sign_in_with_password({
            "email": email.strip(),
            "password": password,
        })

        if res.user and res.session:
            user_data = {
                "id": res.user.id,
                "email": res.user.email,
                "full_name": (res.user.user_metadata or {}).get("full_name", ""),
            }
            # Record user session safely without storing raw password
            st.session_state["authenticated"] = True
            st.session_state["user_session"] = user_data
            st.session_state["user_email"] = res.user.email
            st.session_state["user_name"] = user_data["full_name"] or res.user.email.split("@")[0]
            st.session_state["preview_mode"] = False

            return {
                "success": True,
                "user": user_data,
                "session": res.session,
                "error": None,
            }
        else:
            return {
                "success": False,
                "error": "Authentication failed: No active session received.",
                "unconfigured": False,
            }
    except Exception as e:
        err_msg = str(e)
        if "invalid login credentials" in err_msg.lower() or "invalid_grant" in err_msg.lower():
            err_msg = "Invalid email or password. Please verify your credentials."
        elif "email not confirmed" in err_msg.lower():
            err_msg = "Please confirm your email address before logging in. Check your inbox for the verification link."
        return {
            "success": False,
            "error": err_msg,
            "unconfigured": False,
        }


def reset_password(email: str, redirect_to: Optional[str] = None) -> Dict[str, Any]:
    """Request a password reset email via Supabase."""
    if not is_auth_configured():
        return {
            "success": False,
            "error": "Authentication provider is not yet configured.",
            "unconfigured": True,
        }

    client = get_auth_client()
    if not client:
        return {
            "success": False,
            "error": "Unable to connect to authentication client.",
            "unconfigured": True,
        }

    try:
        kwargs = {}
        if redirect_to:
            kwargs["redirect_to"] = redirect_to

        client.auth.reset_password_for_email(email.strip(), kwargs)
        return {
            "success": True,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "unconfigured": False,
        }


def update_password(new_password: str) -> Dict[str, Any]:
    """Update password for an authenticated or recovery session."""
    if not is_auth_configured():
        return {
            "success": False,
            "error": "Authentication provider is not yet configured.",
            "unconfigured": True,
        }

    client = get_auth_client()
    if not client:
        return {
            "success": False,
            "error": "Unable to connect to authentication client.",
            "unconfigured": True,
        }

    try:
        client.auth.update_user({"password": new_password})
        return {
            "success": True,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "unconfigured": False,
        }


def sign_out():
    """Sign out the current user and clear session state."""
    client = get_auth_client()
    if client:
        try:
            client.auth.sign_out()
        except Exception:
            pass

    st.session_state["authenticated"] = False
    st.session_state["preview_mode"] = False
    st.session_state.pop("user_session", None)
    st.session_state.pop("user_email", None)
    st.session_state.pop("user_name", None)
    st.session_state["current_page"] = "landing"
    st.session_state["_last_query_page"] = "landing"
    try:
        st.query_params["page"] = "landing"
    except Exception:
        pass
