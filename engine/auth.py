"""Accounts backed by Supabase Auth, shared by the hood UI and the
overlay: signup, login, and a "remember me" session (a locally-cached
refresh token) so you don't have to log in every time you launch
Jarvis. Requires internet access and a configured Supabase project --
see the README's Supabase setup section.
"""

import json
import os
import platform

from engine.db import SupabaseNotConfigured, get_client

APP_NAME = "Jarvis"

_current_user = None  # {"name": ..., "email": ...} for this running process


class AuthError(Exception):
    """Raised for user-facing signup/login problems."""


def _app_data_dir():
    """Where the local "remember me" refresh token is cached. Nothing
    else is stored locally anymore -- accounts themselves live in
    Supabase."""
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


def _session_path():
    return os.path.join(_app_data_dir(), "session.json")


def _user_dict(user):
    name = (user.user_metadata or {}).get("full_name") or user.email
    return {"id": user.id, "name": name, "email": user.email}


def _save_local_session(session):
    with open(_session_path(), "w", encoding="utf-8") as handle:
        json.dump({"refresh_token": session.refresh_token}, handle)


def _friendly_error(exc):
    message = str(exc).lower()
    if "already registered" in message or "already exists" in message:
        return "An account with that email already exists."
    if "invalid login credentials" in message:
        return "Incorrect email or password."
    if "password" in message and ("6" in message or "short" in message or "weak" in message):
        return "Password must be at least 6 characters."
    if "rate limit" in message:
        return "Too many attempts -- please wait a moment and try again."
    return str(exc)


def signup(name, email, password):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""

    if not name:
        raise AuthError("Please enter your name.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise AuthError("Please enter a valid email address.")
    if len(password) < 6:
        raise AuthError("Password must be at least 6 characters.")

    try:
        client = get_client()
        response = client.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {"data": {"full_name": name}},
            }
        )
    except SupabaseNotConfigured:
        raise
    except Exception as exc:
        raise AuthError(_friendly_error(exc))

    if not response.session:
        raise AuthError(
            "Account created -- check your email to confirm it, then log in. "
            "(Your Supabase project can disable this step in Authentication "
            "settings if you'd rather skip it.)"
        )

    _save_local_session(response.session)
    user = _user_dict(response.user)
    set_current_user(user)
    return user


def login(email, password):
    email = (email or "").strip().lower()
    password = password or ""

    try:
        client = get_client()
        response = client.auth.sign_in_with_password({"email": email, "password": password})
    except SupabaseNotConfigured:
        raise
    except Exception as exc:
        raise AuthError(_friendly_error(exc))

    _save_local_session(response.session)
    user = _user_dict(response.user)
    set_current_user(user)
    return user


def get_remembered_session():
    """Return {name, email} for the remembered session, or None."""
    path = _session_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            cached = json.load(handle)
    except (OSError, ValueError):
        return None

    refresh_token = cached.get("refresh_token")
    if not refresh_token:
        return None

    try:
        client = get_client()
        response = client.auth.refresh_session(refresh_token)
    except SupabaseNotConfigured:
        raise
    except Exception as exc:
        print(f"Could not restore session: {exc}")
        try:
            os.remove(path)
        except OSError:
            pass
        return None

    if not response.session:
        return None

    _save_local_session(response.session)
    user = _user_dict(response.user)
    set_current_user(user)
    return user


def logout():
    try:
        get_client().auth.sign_out()
    except SupabaseNotConfigured:
        pass
    except Exception as exc:
        print(f"Sign-out request failed (clearing local session anyway): {exc}")
    try:
        os.remove(_session_path())
    except OSError:
        pass
    set_current_user(None)


def get_current_user():
    """The account active in THIS process. Set on signup/login/remembered-
    session restore; used by engine.projects and engine.tutor to scope
    data to whoever is currently using this Jarvis process."""
    return _current_user


def set_current_user(user):
    global _current_user
    _current_user = user
