import re
import sqlite3

from app.config import DB_PATH

try:
    import mysql.connector
    HAS_MYSQL = True
except ImportError:
    HAS_MYSQL = False


class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, sql, params=None):
        if "%s" in sql:
            sql = sql.replace("%s", "?")
        if "AS CHAR" in sql.upper():
            sql = re.sub(r"AS\s+CHAR", "AS TEXT", sql, flags=re.IGNORECASE)
        if params is not None:
            return self._cursor.execute(sql, params)
        return self._cursor.execute(sql)

    def executemany(self, sql, params_list):
        if "%s" in sql:
            sql = sql.replace("%s", "?")
        if "AS CHAR" in sql.upper():
            sql = re.sub(r"AS\s+CHAR", "AS TEXT", sql, flags=re.IGNORECASE)
        return self._cursor.executemany(sql, params_list)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size=None):
        if size is not None:
            return self._cursor.fetchmany(size)
        return self._cursor.fetchmany()

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        return self._cursor.close()

    def __iter__(self):
        return iter(self._cursor)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn
        try:
            self._conn.create_function("CONCAT", -1, lambda *args: "".join(str(a) if a is not None else "" for a in args))
            self._conn.create_function("concat", -1, lambda *args: "".join(str(a) if a is not None else "" for a in args))
        except Exception:
            pass

    def cursor(self, *args, **kwargs):
        return SQLiteCursorWrapper(self._conn.cursor(*args, **kwargs))

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


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
    raw_conn = sqlite3.connect(str(DB_PATH))
    return SQLiteConnectionWrapper(raw_conn)

