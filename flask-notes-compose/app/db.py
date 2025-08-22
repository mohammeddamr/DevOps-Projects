import os
import mysql.connector

def _cfg():
    return {
        "host": os.getenv("MYSQL_HOST", "db"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "notes_user"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "notes"),
    }

def get_connection():
    return mysql.connector.connect(**_cfg())

def ensure_schema():
    """Idempotent migration: creates table if missing."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
    """)
    conn.commit()
    cur.close()
    conn.close()
