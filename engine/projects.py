"""Named workspaces backed by Supabase Postgres. Each project keeps its
own chat memory (engine.tutor) and its own notes folder (engine.notes),
so you can separate "the novel I'm writing" from "my tax questions"
instead of one long tangled conversation.

Row-level security on the `projects` table means every query here is
already scoped to whoever is signed in -- Postgres itself refuses to
return or accept rows for anyone else, so there's no user_id filtering
needed on reads.
"""

from engine.auth import get_current_user
from engine.db import get_client

DEFAULT_PROJECT = {"id": None, "name": "General"}

_current_project_by_user = {}  # user id -> project dict, in-memory per process


def slugify(name):
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return slug or "project"


def list_projects():
    """Return this user's projects, or [] if not signed in / unavailable."""
    user = get_current_user()
    if not user:
        return []
    try:
        client = get_client()
        response = client.table("projects").select("id, name").order("created_at").execute()
        return response.data or []
    except Exception as exc:
        print(f"Could not list projects: {exc}")
        return []


def create_project(name):
    name = (name or "").strip()
    if not name:
        raise ValueError("Give the project a name.")

    user = get_current_user()
    if not user:
        raise ValueError("You need to be logged in to create a project.")

    client = get_client()
    try:
        response = (
            client.table("projects")
            .insert({"user_id": user["id"], "name": name})
            .execute()
        )
    except Exception as exc:
        message = str(exc)
        if "duplicate" in message.lower() or "unique" in message.lower():
            raise ValueError("You already have a project with that name.")
        raise ValueError(f"Could not create the project: {exc}")

    return response.data[0]


def get_current_project():
    user = get_current_user()
    if not user:
        return DEFAULT_PROJECT
    return _current_project_by_user.get(user["id"], DEFAULT_PROJECT)


def set_current_project(project):
    user = get_current_user()
    if not user:
        return
    _current_project_by_user[user["id"]] = project or DEFAULT_PROJECT


def history_key():
    """A key identifying "this user's current project", for scoping
    in-memory conversation history (engine.tutor) and notes (engine.notes)."""
    user = get_current_user()
    if not user:
        return "anonymous:general"
    project = get_current_project()
    return f"{user['id']}:{project['id'] or 'general'}"
