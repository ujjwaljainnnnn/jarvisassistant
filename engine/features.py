import os
import datetime
import webbrowser
from urllib.parse import quote_plus

import eel
from playsound import playsound

from engine.config import ASSISTANT_NAME
from engine.command import speak

SOUND_PATH = os.path.join(os.path.dirname(__file__), "..", "www", "assets", "audio", "audio_notification.mp3")

# Websites Jarvis can open by name
WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "linkedin": "https://www.linkedin.com",
}


@eel.expose
def playAssistantSound():
    playsound(os.path.abspath(SOUND_PATH))


def openCommand(query):
    """'open youtube' → website, 'open notepad' → local app (Windows)."""
    target = query.replace(ASSISTANT_NAME.lower(), "").replace("open", "").strip().lower()

    if not target:
        speak("Sorry, I didn't catch what to open")
        return

    if target in WEBSITES:
        speak("Opening " + target)
        webbrowser.open(WEBSITES[target])
    else:
        speak("Opening " + target)
        os.system("start " + target)


def tellTime():
    now = datetime.datetime.now()
    speak("It is " + now.strftime("%I:%M %p"))


def tellDate():
    today = datetime.date.today()
    speak("Today is " + today.strftime("%A, %d %B %Y"))


def searchGoogle(query):
    term = query.replace("search", "").replace("google", "").replace("for", "", 1).strip()
    speak("Searching Google for " + term)
    webbrowser.open("https://www.google.com/search?q=" + quote_plus(term))


def playYoutube(query):
    term = query.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
    speak("Playing " + term + " on YouTube")
    webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(term))
