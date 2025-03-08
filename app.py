import os
import dotenv
import authlib
import birthday
import requests
import tempfile
import streamlit as st
import mysql.connector
import birthday_email_notifier
from authlib.integrations.requests_client import OAuth2Session

# Load environment variables
dotenv.load_dotenv()

# Retrieve the admin email from the environment variables
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

def get_connection():
    """
    Establishes and returns a secure MySQL database connection using SSL.
    The SSL CA certificate is obtained from the 'AIVEN_CA_PEM' environment variable.

    Raises:
        EnvironmentError: If the SSL certificate content is not provided.
        mysql.connector.Error: If the database connection fails.
    """
    # Retrieve the SSL CA certificate content from the environment variable
    ssl_ca_content = os.getenv("AIVEN_CA_PEM")
    if not ssl_ca_content:
        st.error("SSL CA certificate not found in environment variable 'AIVEN_CA_PEM'")
        raise EnvironmentError("SSL CA certificate not found in environment variable 'AIVEN_CA_PEM'")

    # Write the certificate content to a secure temporary file with a .pem extension
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".pem") as tmp_file:
        tmp_file.write(ssl_ca_content)
        ssl_ca_path = tmp_file.name

    # Set file permissions to allow read access only to the file owner
    os.chmod(ssl_ca_path, 0o600)

    try:
        # Establish a secure connection to the MySQL database using the temporary certificate file
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            ssl_ca=ssl_ca_path,
            ssl_verify_cert=True,
            connection_timeout=10,
            tls_versions=["TLSv1.2"],
            use_pure=True
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"MySQL connection failed: {e}")
        raise

def load_authorized_emails():
    """
    Retrieve and return the set of authorized emails from the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM authorized_emails")
    results = cursor.fetchall()
    emails = {row[0] for row in results}
    cursor.close()
    conn.close()
    return emails


def add_authorized_email(email):
    """
    Add a new authorized email to the database.

    Args:
        email (str): The email address to add.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO authorized_emails (email) VALUES (%s)", (email,))
    conn.commit()
    cursor.close()
    conn.close()


def remove_authorized_email(email):
    """
    Remove an authorized email from the database.

    Args:
        email (str): The email address to remove.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM authorized_emails WHERE email = %s", (email,))
    conn.commit()
    cursor.close()
    conn.close()


# --- Google OAuth Configuration ---
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = ["openid", "email", "profile"]

oauth_client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, scope=SCOPE, redirect_uri=REDIRECT_URI)

# --- Session State Initialization ---
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


def rerun():
    """
    Rerun the Streamlit app.
    """
    try:
        st.experimental_rerun()
    except AttributeError:
        try:
            from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx, RerunException
            raise RerunException(get_script_run_ctx())
        except Exception:
            pass


# --- Enhanced UI Styles ---
st.markdown(
    """
    <style>
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
    """
    Display the OAuth login interface and redirect the user to Google's authorization page.
    """
    auth_url, state = oauth_client.create_authorization_url(AUTHORIZATION_URL)
    st.session_state["oauth_state"] = state

    st.markdown('<p class="big-font">🎂 Welcome to Birthday Finder! 🎂</p>', unsafe_allow_html=True)
    st.markdown('<p class="small-font">Login with Google to continue</p>', unsafe_allow_html=True)

    if st.button("🔑 Login with Google"):
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={auth_url}">', unsafe_allow_html=True)


def fetch_user_info():
    """
    Process the OAuth callback, fetch the user's information, and verify their authorization.
    """
    # Skip OAuth processing if already logged in
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

            if email in load_authorized_emails():
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
    """
    Log out the current user and reset the session state.
    """
    st.session_state["logged_in_user"] = None
    st.session_state["user_name"] = None
    st.session_state["profile_pic"] = None
    st.session_state["logged_in"] = False
    st.session_state["page"] = "login"


def admin_panel():
    """
    Display the admin panel for managing authorized emails.
    """
    authorized_emails = load_authorized_emails()
    st.markdown("## Admin: Manage Authorized Emails")
    st.write("Currently authorized emails:")
    for email in sorted(authorized_emails):
        st.write(email)
        if st.button(f"Remove {email}", key=f"remove_{email}"):
            if email == ADMIN_EMAIL:
                st.warning("Cannot remove admin email!")
            else:
                remove_authorized_email(email)
                st.success(f"Removed {email}")
                rerun()
    new_email = st.text_input("Add new authorized email", key="new_email_input")
    if st.button("Add Email"):
        if new_email:
            add_authorized_email(new_email)
            st.success(f"Added {new_email}")
            rerun()


def dashboard():
    """
    Render the personalized dashboard for the logged-in user.
    """
    if not st.session_state.get("logged_in", False):
        st.warning("⚠️ Unauthorized access. Please login.")
        return

    user_name = st.session_state["user_name"]
    user_email = st.session_state["logged_in_user"]

    st.markdown(f'<p class="big-font">🎉 Welcome, {user_name}! 🎉</p>', unsafe_allow_html=True)

    if st.session_state.get("profile_pic"):
        st.image(st.session_state["profile_pic"], width=140, caption=user_name)

    df = birthday.get_dataframe()

    if not df.empty:
        st.write("Here are today's birthdays:")
        st.dataframe(df.style.set_properties(**{'text-align': 'center'}))
    else:
        st.markdown('<p class="small-font">🎊 No birthdays today! Enjoy your day! 🎊</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.button("🚪 Logout", on_click=logout, key="logout_button")
    with col2:
        if st.button("🔄 Refresh Birthdays"):
            rerun()

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown('<p class="small-font">Would you like a copy of these responses via email?</p>', unsafe_allow_html=True)
    if st.button("📧 Email me a copy"):

        if birthday_email_notifier.send_email(user_name, user_email):
            st.success("A copy of the responses has been sent to your email!")
        else:
            st.error(f"Failed to send email")

    st.markdown('<p class="small-font">Refresh the page to log in as a different user.</p>', unsafe_allow_html=True)

    if st.session_state.get("logged_in_user") == ADMIN_EMAIL:
        admin_panel()


# --- Main Application Flow ---
fetch_user_info()

if st.session_state["page"] == "dashboard":
    dashboard()
else:
    login()
