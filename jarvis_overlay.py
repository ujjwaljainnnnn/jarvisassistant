"""Entry point for the floating cursor-companion / digital tutor.

Run this instead of main.py to get an always-on-top glowing dot that
follows your mouse, listens for voice questions, and answers with
awareness of whatever window you currently have focused -- no
screenshots or tab-switching required.

Usage:
    python jarvis_overlay.py

Optional:
    ANTHROPIC_API_KEY  - set this to let unanswered questions be routed
                          to Claude for a real answer instead of the
                          built-in offline tips.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from overlay.floating_icon import run

if __name__ == "__main__":
    run()
