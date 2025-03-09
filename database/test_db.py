import os
import dotenv
import logging
import tempfile
import mysql.connector

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def validate_env():
    """Validate that all required environment variables are set."""
    required_vars = ["MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

def main():
    """Main function to test MySQL connection and fetch data."""
    try:
        validate_env()

        ssl_ca_content = os.getenv("AIVEN_CA_PEM")

        # Write the certificate content to a secure temporary file with a .pem extension
        with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".pem") as tmp_file:
            tmp_file.write(ssl_ca_content)
            ssl_ca_path = tmp_file.name

        # Set file permissions to allow read access only to the file owner
        os.chmod(ssl_ca_path, 0o600)

        # Establish MySQL connection
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
        logger.info("Connected to MySQL with SSL verification.")
    except mysql.connector.Error as e:
        logger.error("Database connection error:", exc_info=True)
        return

    try:
        cur = conn.cursor()

        # Query authorized_emails table
        cur.execute("SELECT email FROM authorized_emails")
        rows = cur.fetchall()

        if rows:
            logger.info("Rows in 'authorized_emails' table:")
            for r in rows:
                logger.info(r)
        else:
            logger.info("No rows found in 'authorized_emails' table.")

        # Query email_schedule table
        cur.execute("SELECT email, scheduling_enabled FROM email_schedule")
        schedule_rows = cur.fetchall()

        if schedule_rows:
            logger.info("Rows in 'email_schedule' table:")
            for row in schedule_rows:
                logger.info(row)
        else:
            logger.info("No rows found in 'email_schedule' table.")
    except mysql.connector.Error as e:
        logger.error("Query execution error:", exc_info=True)
    finally:
        cur.close()
        conn.close()
        logger.info("Connection closed.")

if __name__ == "__main__":
    main()
