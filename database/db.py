import sqlite3

from app.config import DB_PATH

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False


def connect_db():
    """
    Connect to database.
    Attempts MySQL connection first.
    Falls back to SQLite database (airline.db) if MySQL connection fails.
    """
    if HAS_MYSQL:
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="",  # Update password if configured
                database="airline_db",
            )
        except Exception:
            pass

    # Fallback to SQLite
    return sqlite3.connect(str(DB_PATH))
