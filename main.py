import os
import sys
import threading
import webbrowser

import eel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.features import playAssistantSound
from engine import command  # noqa: F401 -- registers eel.expose(allCommands)
from engine import account  # noqa: F401 -- registers eel.expose(loginUser/signupUser/...)

eel.init("www")

playAssistantSound()

PORT = 8000


def open_browser():
    try:
        webbrowser.open(f"http://localhost:{PORT}/index.html")
    except webbrowser.Error as exc:
        print(f"Could not open a browser automatically: {exc}")
        print(f"Open http://localhost:{PORT}/index.html manually.")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    eel.start("index.html", mode=None, host="localhost", port=PORT, block=True)
