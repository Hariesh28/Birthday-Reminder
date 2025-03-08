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

    # 1) Create the table if it doesn't exist
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS authorized_emails (
        email VARCHAR(255) PRIMARY KEY
    )
    """
    cursor.execute(create_table_sql)

    # 2) Insert the admin email if not already present
    insert_sql = """
    INSERT IGNORE INTO authorized_emails (email)
    VALUES (%s)
    """

    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')

    cursor.execute(insert_sql, (ADMIN_EMAIL,))

    conn.commit()
    cursor.close()
    conn.close()

    print("Setup complete! The 'authorized_emails' table was created (if needed), and 'hariesh28606@gmail.com' has been inserted.")

if __name__ == "__main__":
    main()
