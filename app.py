import os
import json
import dotenv
import authlib
import birthday
import requests
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

dotenv.load_dotenv()

# Google OAuth Configuration
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://localhost:8501"
SCOPE = ["openid", "email", "profile"]

oauth_client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, scope=SCOPE, redirect_uri=REDIRECT_URI)

def load_authorized_emails():
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
            return set(data.get("AUTHORIZED_EMAILS", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

AUTHORIZED_EMAILS = load_authorized_emails()

# Initialize session state
if "logged_in_user" not in st.session_state:
    st.session_state["logged_in_user"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "profile_pic" not in st.session_state:
    st.session_state["profile_pic"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# Helper function for rerunning the app
def rerun():
    try:
        st.experimental_rerun()
    except AttributeError:
        try:
            from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx, RerunException # type: ignore
            raise RerunException(get_script_run_ctx())
        except Exception:
            pass  # Fallback: do nothing

# 🎨 Enhanced UI Styles
st.markdown(
    """
    <style>
        /* Overall body style */
        body {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .big-font {
            font-size: 48px !important;
            text-align: center;
            font-weight: bold;
            color: #343a40;
            margin-top: 30px;
            animation: fadeIn 1.5s ease-in-out;
        }
        .small-font {
            font-size: 24px !important;
            text-align: center;
            color: #6c757d;
            margin-bottom: 30px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #ff7e67, #ff4081);
            color: white;
            font-size: 20px;
            padding: 14px 28px;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.05);
        }
        .profile-pic {
            display: block;
            margin: 20px auto;
            border-radius: 50%;
            width: 140px;
            height: 140px;
            border: 4px solid #ff4081;
        }
        .birthday-box {
            background: #ffe0f0;
            padding: 20px;
            margin: 20px auto;
            border-radius: 12px;
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            color: #ff4081;
            animation: fadeIn 1.5s ease-in-out;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def login():
    """OAuth login button with redirection handling."""
    auth_url, state = oauth_client.create_authorization_url(AUTHORIZATION_URL)
    st.session_state["oauth_state"] = state

    st.markdown('<p class="big-font">🎂 Welcome to Birthday Finder! 🎂</p>', unsafe_allow_html=True)
    st.markdown('<p class="small-font">Login with Google to continue</p>', unsafe_allow_html=True)

    if st.button("🔑 Login with Google"):
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={auth_url}">', unsafe_allow_html=True)

def fetch_user_info():
    """Fetch user info after login and check authorization."""
    # If already logged in, skip processing OAuth code in query params
    if st.session_state.get("logged_in", False):
        return

    query_params = st.query_params
    if "code" in query_params:
        try:
            token = oauth_client.fetch_token(
                TOKEN_URL,
                authorization_response=f"{REDIRECT_URI}?code={query_params['code']}",
                include_client_id=True
            )

            user_info = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token['access_token']}"},
            ).json()

            email = user_info.get("email", "")
            name = user_info.get("name", "User")
            picture = user_info.get("picture", None)

            if email in AUTHORIZED_EMAILS:
                st.session_state["logged_in_user"] = email
                st.session_state["user_name"] = name
                st.session_state["profile_pic"] = picture
                st.session_state["logged_in"] = True
                st.session_state["page"] = "dashboard"
            else:
                st.session_state["logged_in"] = False
                st.warning("⚠️ You are not authorized to access this dashboard.")

        except requests.exceptions.RequestException as e:
            st.error(f"OAuth request failed: {e}")
        except authlib.integrations.base_client.errors.OAuthError:
            st.session_state["page"] = "login"
            rerun()

def logout():
    """Clear session state to log out the user."""
    st.session_state["logged_in_user"] = None
    st.session_state["user_name"] = None
    st.session_state["profile_pic"] = None
    st.session_state["logged_in"] = False
    st.session_state["page"] = "login"

def dashboard():
    """Personalized dashboard with enhanced UI."""
    if not st.session_state.get("logged_in", False):
        st.warning("⚠️ Unauthorized access. Please login.")
        return

    user_name = st.session_state["user_name"]
    st.markdown(f'<p class="big-font">🎉 Welcome, {user_name}! 🎉</p>', unsafe_allow_html=True)

    # Display profile picture if available
    if st.session_state.get("profile_pic"):
        st.image(st.session_state["profile_pic"], width=140, caption=user_name)

    st.write("Here are today's birthdays:")
    df = birthday.get_dataframe()

    if not df.empty:
        st.dataframe(df.style.set_properties(**{'text-align': 'center'}))
    else:
        st.markdown('<p class="small-font">🎊 No birthdays today! Enjoy your day! 🎊</p>', unsafe_allow_html=True)

    # Use on_click callback for logout so it immediately logs out on one click.
    col1, col2 = st.columns(2)
    with col1:
        st.button("🚪 Logout", on_click=logout, key="logout_button")
    with col2:
        if st.button("🔄 Refresh Birthdays"):
            rerun()

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<p class="small-font">Refresh the page to log in as a different user.</p>', unsafe_allow_html=True)

# Run the login flow
fetch_user_info()

if st.session_state["page"] == "dashboard":
    dashboard()
else:
    login()
