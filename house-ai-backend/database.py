
import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


SESSION_DAYS = 30


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def db():
    """Connect to PostgreSQL, commit changes, and close connection."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ---------------- Initialize Database ----------------

def init_db():
    """Create tables if they do not already exist."""

    with db() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


# ---------------- Users ----------------

def create_user(name, email, password_hash):

    with db() as conn:
        conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (name, email, password_hash)
        )

        return conn.fetchone()["id"]


def get_user_by_email(email):

    with db() as conn:
        conn.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        return conn.fetchone()


# ---------------- Login Sessions ----------------

def create_session(user_id):

    token = secrets.token_hex(32)

    expires_at = (
        datetime.now(timezone.utc) +
        timedelta(days=SESSION_DAYS)
    ).isoformat()

    with db() as conn:
        conn.execute(
            """
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (%s, %s, %s)
            """,
            (token, user_id, expires_at)
        )

    return token


def get_user_by_token(token):

    with db() as conn:
        conn.execute(
            """
            SELECT users.id, users.name, users.email
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = %s
            AND sessions.expires_at > %s
            """,
            (token, now())
        )

        return conn.fetchone()


def delete_session(token):

    with db() as conn:
        conn.execute(
            "DELETE FROM sessions WHERE token = %s",
            (token,)
        )


# ---------------- Query History ----------------

def save_query(user_id, query, answer):

    with db() as conn:
        conn.execute(
            """
            INSERT INTO queries (user_id, query, answer, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (user_id, query, answer, now())
        )

        return conn.fetchone()["id"]


def get_history(user_id):

    with db() as conn:
        conn.execute(
            """
            SELECT id, query,
                   LEFT(answer, 160) AS preview,
                   created_at
            FROM queries
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (user_id,)
        )

        return conn.fetchall()


def get_history_item(user_id, query_id):

    with db() as conn:
        conn.execute(
            """
            SELECT id, query, answer, created_at
            FROM queries
            WHERE id = %s AND user_id = %s
            """,
            (query_id, user_id)
        )

        return conn.fetchone()
