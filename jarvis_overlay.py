"""Entry point for the floating cursor-companion / digital tutor.

Run this instead of main.py to get an always-on-top glowing dot that
follows your mouse, listens for voice questions, and answers with
awareness of whatever window you currently have focused -- no
screenshots or tab-switching required. Say "take notes" to have it turn
a rambling voice note into clean, organized notes.

Usage:
    python jarvis_overlay.py

Optional:
    ANTHROPIC_API_KEY  - set this to let unanswered questions -- and note
                          organizing -- be routed to Claude for a real
                          answer instead of the built-in offline tips.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication

from overlay.auth_dialog import ensure_logged_in
from overlay.floating_icon import run

if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)

    session = ensure_logged_in()
    if not session:
        sys.exit(0)

    run(app=app, user=session)
