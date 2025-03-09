import os
import dotenv
import mysql.connector

dotenv.load_dotenv()

def main():
    # Read environment variables for DB credentials
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "defaultdb")

    # Connect to MySQL
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()

    # 1) Create the authorized_emails table if it doesn't exist
    create_authorized_emails_sql = """
    CREATE TABLE IF NOT EXISTS authorized_emails (
        email VARCHAR(255) PRIMARY KEY
    );
    """
    cursor.execute(create_authorized_emails_sql)

    # 2) Create the email_schedule table if it doesn't exist
    create_email_schedule_sql = """
    CREATE TABLE IF NOT EXISTS email_schedule (
        email VARCHAR(255) PRIMARY KEY,
        scheduling_enabled TINYINT(1) NOT NULL DEFAULT 1
    );
    """
    cursor.execute(create_email_schedule_sql)

    # 3) Insert the admin email into authorized_emails if not already present
    insert_sql = """
    INSERT IGNORE INTO authorized_emails (email)
    VALUES (%s);
    """
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')
    cursor.execute(insert_sql, (ADMIN_EMAIL,))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Setup complete! Tables 'authorized_emails' and 'email_schedule' have been created (if needed), and admin email ({ADMIN_EMAIL}) has been inserted.")

if __name__ == "__main__":
    main()
