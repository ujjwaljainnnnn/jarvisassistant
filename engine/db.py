"""Shared Supabase client -- Jarvis's backend for accounts, projects,
and notes. See the README's Supabase setup section for how to create
your own project and configure SUPABASE_URL / SUPABASE_ANON_KEY.
"""

import os

_client = None


class SupabaseNotConfigured(RuntimeError):
    """Raised when SUPABASE_URL / SUPABASE_ANON_KEY aren't set."""


def is_configured():
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_ANON_KEY"))


def get_client():
    """Return a shared Supabase client, creating it on first use.

    The client is re-created if the current one isn't signed in but a
    session should exist -- callers manage auth state via engine.auth.
    """
    global _client
    if _client is None:
        if not is_configured():
            raise SupabaseNotConfigured(
                "Jarvis needs SUPABASE_URL and SUPABASE_ANON_KEY set to run. "
                "See the README's 'Supabase setup' section."
            )
        from supabase import create_client

        _client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
    return _client
