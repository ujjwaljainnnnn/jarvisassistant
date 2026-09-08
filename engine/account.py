"""Eel-exposed bindings onto engine.auth for the browser hood UI."""

import eel

from engine import auth
from engine.db import SupabaseNotConfigured

NOT_CONFIGURED_MESSAGE = (
    "Jarvis isn't connected to a database yet. Set SUPABASE_URL and "
    "SUPABASE_ANON_KEY (see the README's Supabase setup section) and restart."
)


@eel.expose
def signupUser(name, email, password):
    try:
        session = auth.signup(name, email, password)
        return {"success": True, "name": session["name"], "email": session["email"]}
    except SupabaseNotConfigured:
        return {"success": False, "message": NOT_CONFIGURED_MESSAGE}
    except auth.AuthError as exc:
        return {"success": False, "message": str(exc)}
    except Exception as exc:
        print(f"Signup failed: {exc}")
        return {"success": False, "message": "Something went wrong. Please try again."}


@eel.expose
def loginUser(email, password):
    try:
        session = auth.login(email, password)
        return {"success": True, "name": session["name"], "email": session["email"]}
    except SupabaseNotConfigured:
        return {"success": False, "message": NOT_CONFIGURED_MESSAGE}
    except auth.AuthError as exc:
        return {"success": False, "message": str(exc)}
    except Exception as exc:
        print(f"Login failed: {exc}")
        return {"success": False, "message": "Something went wrong. Please try again."}


@eel.expose
def getRememberedUser():
    try:
        return auth.get_remembered_session()
    except SupabaseNotConfigured as exc:
        print(f"Not signed in: {exc}")
        return None


@eel.expose
def logoutUser():
    from engine.tutor import reset_conversation

    auth.logout()
    reset_conversation()
    return {"success": True}
