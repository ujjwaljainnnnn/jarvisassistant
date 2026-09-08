"""Eel-exposed bindings onto engine.auth for the browser hood UI."""

import eel

from engine import auth


@eel.expose
def signupUser(name, email, password):
    try:
        session = auth.signup(name, email, password)
        return {"success": True, "name": session["name"], "email": session["email"]}
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
    except auth.AuthError as exc:
        return {"success": False, "message": str(exc)}
    except Exception as exc:
        print(f"Login failed: {exc}")
        return {"success": False, "message": "Something went wrong. Please try again."}


@eel.expose
def getRememberedUser():
    return auth.get_remembered_session()


@eel.expose
def logoutUser():
    from engine.tutor import reset_conversation

    auth.logout()
    reset_conversation()
    return {"success": True}
