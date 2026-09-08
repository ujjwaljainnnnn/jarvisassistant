"""Entry point for the floating cursor-companion / digital tutor.

Run this instead of main.py to get an always-on-top glowing dot that
follows your mouse, listens for voice questions, and answers with
awareness of whatever window you currently have focused -- no
screenshots or tab-switching required. Say "take notes" to have it turn
a rambling voice note into clean, organized notes.

Usage:
    python jarvis_overlay.py

Required -- Jarvis signs you in and stores projects/notes via Supabase;
see the README's "Supabase setup" section:
    SUPABASE_URL       - your Supabase project's API URL
    SUPABASE_ANON_KEY  - your project's anon/publishable key

Optional -- set one of these to let unanswered questions (and note
organizing) be routed to a real model instead of the built-in offline
tips:
    ANTHROPIC_API_KEY  - Claude
    OPENAI_API_KEY     - ChatGPT
    GEMINI_API_KEY     - Gemini
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.db import is_configured

if not is_configured():
    sys.exit(
        "Jarvis needs a Supabase project to sign you in and store your "
        "projects/notes.\n\n"
        "Set these environment variables and try again:\n"
        "  SUPABASE_URL=https://<your-project-ref>.supabase.co\n"
        "  SUPABASE_ANON_KEY=<your project's anon/publishable key>\n\n"
        "See the README's 'Supabase setup' section for step-by-step instructions."
    )

from PyQt5.QtWidgets import QApplication

from overlay.auth_dialog import ensure_logged_in
from overlay.floating_icon import run

if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)

    session = ensure_logged_in()
    if not session:
        sys.exit(0)

    run(app=app, user=session)
