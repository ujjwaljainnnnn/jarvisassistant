import os
import sys
import threading
import webbrowser

import eel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.features import playAssistantSound
from engine import command  # noqa: F401 -- registers eel.expose(allCommands)

eel.init("www")

playAssistantSound()

PORT = 8000


def open_browser():
    webbrowser.open(f"http://localhost:{PORT}/index.html")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    eel.start("index.html", mode=None, host="localhost", port=PORT, block=True)
