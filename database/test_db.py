import os
import dotenv
import logging
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

        # Establish MySQL connection
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            ssl_ca="aiven-ca.pem",
            ssl_verify_cert=True,
            tls_versions=["TLSv1.2"],  # Explicit TLS version for security
            use_pure=True  # Ensures compatibility with some MySQL setups
        )
        logger.info("Connected to MySQL with SSL verification.")

    except mysql.connector.Error as e:
        logger.error("Database connection error:", exc_info=True)
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT email FROM authorized_emails")
        rows = cur.fetchall()

        if rows:
            logger.info("Rows in table:")
            for r in rows:
                logger.info(r)
        else:
            logger.info("No rows found.")

    except mysql.connector.Error as e:
        logger.error("Query execution error:", exc_info=True)

    finally:
        cur.close()
        conn.close()
        logger.info("Connection closed.")

if __name__ == "__main__":
    main()
