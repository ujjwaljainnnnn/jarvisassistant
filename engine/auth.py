"""Local account system shared by the hood UI and the overlay: signup,
login, and a "remember me" session so you don't have to log in every
time you launch Jarvis. Passwords are never stored in plain text --
each is hashed with PBKDF2-HMAC-SHA256 and a random per-user salt.

This is a single-machine, single-app account store (SQLite in the OS's
per-user app-data folder), meant to give Jarvis a real login/signup flow
and a personalized greeting -- not a network-facing auth boundary.
"""

import hashlib
import hmac
import os
import platform
import sqlite3
import time
import uuid

APP_NAME = "Jarvis"
PBKDF2_ITERATIONS = 200_000


class AuthError(Exception):
    """Raised for user-facing signup/login problems (bad password, etc.)."""


def _app_data_dir():
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def _db_path():
    return os.path.join(_app_data_dir(), "jarvis.db")


def _session_path():
    return os.path.join(_app_data_dir(), "session.txt")


def _get_connection():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


_init_db()


def _hash_password(password, salt_hex):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ITERATIONS
    ).hex()


def _normalize_email(email):
    return (email or "").strip().lower()


def _create_session(conn, user_id, name, email):
    token = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
        (token, user_id, time.time()),
    )
    conn.commit()
    with open(_session_path(), "w", encoding="utf-8") as handle:
        handle.write(token)
    return {"token": token, "name": name, "email": email}


def signup(name, email, password):
    name = (name or "").strip()
    email = _normalize_email(email)
    password = password or ""

    if not name:
        raise AuthError("Please enter your name.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise AuthError("Please enter a valid email address.")
    if len(password) < 6:
        raise AuthError("Password must be at least 6 characters.")

    conn = _get_connection()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise AuthError("An account with that email already exists.")

        salt = os.urandom(16).hex()
        password_hash = _hash_password(password, salt)
        user_id = uuid.uuid4().hex

        conn.execute(
            "INSERT INTO users (id, name, email, salt, password_hash, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, name, email, salt, password_hash, time.time()),
        )
        conn.commit()
        return _create_session(conn, user_id, name, email)
    finally:
        conn.close()


def login(email, password):
    email = _normalize_email(email)
    password = password or ""

    conn = _get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            raise AuthError("No account found with that email.")

        expected_hash = _hash_password(password, row["salt"])
        if not hmac.compare_digest(expected_hash, row["password_hash"]):
            raise AuthError("Incorrect password.")

        return _create_session(conn, row["id"], row["name"], row["email"])
    finally:
        conn.close()


def get_remembered_session():
    """Return {name, email} for the remembered session, or None."""
    path = _session_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            token = handle.read().strip()
    except OSError:
        return None
    if not token:
        return None

    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT users.name AS name, users.email AS email FROM sessions "
            "JOIN users ON users.id = sessions.user_id WHERE sessions.token = ?",
            (token,),
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return None
    return {"name": row["name"], "email": row["email"]}


def logout():
    try:
        os.remove(_session_path())
    except OSError:
        pass
