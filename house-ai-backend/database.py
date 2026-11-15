import os
import sqlite3
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

# Where the database file lives.
# Locally it's just a file called household.db next to this code.
# (On Vercel the disk is read-only except /tmp, and /tmp gets wiped often —
#  see the README for what to use in production.)
if os.getenv("VERCEL"):
    DB_PATH = "/tmp/household.db"
else:
    DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "household.db"))

SESSION_DAYS = 30


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def db():
    """Open the database, save changes when done, then close it."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us read columns by name
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create the three tables if they don't exist yet."""
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                user_id    INTEGER NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                query      TEXT NOT NULL,
                answer     TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


# ---------------- Users ----------------
def create_user(name, email, password_hash):
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        return cursor.lastrowid


def get_user_by_email(email):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()


# ---------------- Login sessions ----------------
def create_session(user_id):
    """Make a random token, remember it, and hand it to the browser."""
    token = secrets.token_hex(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()
    with db() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires_at),
        )
    return token


def get_user_by_token(token):
    """Return the user this token belongs to, or None if it's unknown/expired."""
    with db() as conn:
        return conn.execute(
            """
            SELECT users.id, users.name, users.email
            FROM sessions JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ? AND sessions.expires_at > ?
            """,
            (token, now()),
        ).fetchone()


def delete_session(token):
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


# ---------------- History ----------------
def save_query(user_id, query, answer):
    with db() as conn:
        cursor = conn.execute(
            "INSERT INTO queries (user_id, query, answer, created_at) VALUES (?, ?, ?, ?)",
            (user_id, query, answer, now()),
        )
        return cursor.lastrowid


def get_history(user_id):
    """All of this user's queries, newest first (answer is cut short for the list)."""
    with db() as conn:
        return conn.execute(
            """
            SELECT id, query, substr(answer, 1, 160) AS preview, created_at
            FROM queries WHERE user_id = ? ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()


def get_history_item(user_id, query_id):
    """One query with its full answer. user_id check keeps users out of each other's history."""
    with db() as conn:
        return conn.execute(
            "SELECT id, query, answer, created_at FROM queries WHERE id = ? AND user_id = ?",
            (query_id, user_id),
        ).fetchone()
