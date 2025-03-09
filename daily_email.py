import os
import dotenv
import pytz
import tempfile
from datetime import datetime
import mysql.connector
from birthday_email_notifier import send_email

# Load environment variables from .env file if running locally.
dotenv.load_dotenv()

def get_connection():
    """
    Establish a secure MySQL connection using SSL.
    The SSL certificate is loaded from the environment variable 'AIVEN_CA_PEM'.
    """
    ssl_ca_content = os.getenv("AIVEN_CA_PEM")
    ssl_ca_path = None
    if ssl_ca_content:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".pem") as tmp_file:
            tmp_file.write(ssl_ca_content)
            ssl_ca_path = tmp_file.name
        os.chmod(ssl_ca_path, 0o600)

    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        ssl_ca=ssl_ca_path,
        ssl_verify_cert=True,
        tls_versions=["TLSv1.2"],
        use_pure=True
    )
    return conn

def get_enabled_users():
    """
    Retrieve and return a list of email addresses from 'email_schedule' where
    scheduling_enabled is set to 1.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM email_schedule WHERE scheduling_enabled = 1")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in results]

def main():
    sender_name = os.getenv("SENDER_NAME", "Birthday Reminder")
    enabled_users = get_enabled_users()
    now = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

    if not enabled_users:
        print(f"[{now}] No users with daily email enabled.")
        return

    for user_email in enabled_users:
        success = send_email(sender_name, user_email)
        if success:
            print(f"[{now}] Email sent successfully to {user_email}")
        else:
            print(f"[{now}] Failed to send email to {user_email}")

if __name__ == "__main__":
    main()
