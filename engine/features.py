import os
import platform
import subprocess
import webbrowser

import eel
from playsound import playsound

from engine.config import ASSISTANT_NAME
from engine.speech import speak

WWW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "www")

# Common shortcuts so "open google" / "open youtube" work without a browser
# already being pointed at the right place.
KNOWN_SITES = {
    "google": "https://google.com",
    "youtube": "https://youtube.com",
    "wikipedia": "https://wikipedia.org",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
}


@eel.expose
def playAssistantSound():
    music_path = os.path.join(WWW_DIR, "assets", "audio", "audio_notification.mp3")
    try:
        playsound(music_path)
    except Exception as exc:
        print(f"Could not play assistant sound: {exc}")


def openCommand(query):
    query = query.lower()
    query = query.replace(ASSISTANT_NAME.lower(), "")
    query = query.replace("open", "")
    query = query.strip()

    if not query:
        speak("What should I open?")
        return

    if query in KNOWN_SITES:
        speak(f"Opening {query}")
        webbrowser.open(KNOWN_SITES[query])
        return

    if "." in query and " " not in query:
        # Looks like a domain, e.g. "openai.com".
        speak(f"Opening {query}")
        webbrowser.open(f"https://{query}")
        return

    speak("Opening " + query)
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(query)  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["open", query])
        else:
            subprocess.Popen(["xdg-open", query])
    except Exception:
        speak(f"I could not find {query} on this device.")
