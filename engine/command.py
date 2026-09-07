import os
import time

import eel

from engine import brain, notes
from engine.speech import speak as _speak, listen as _listen

_speak_enabled = True
_active_notes_session = None


def speak(text):
    if _speak_enabled:
        _speak(text, on_speak=eel.DisplayMessage)
    else:
        eel.DisplayMessage(text)


def takeCommand():
    print("Listening...")
    query = _listen(on_status=eel.DisplayMessage)
    if query:
        print(f"User said: {query}")
        time.sleep(1.5)
    return query


def _start_notes_session():
    global _active_notes_session

    def _on_finished(organized_text, _path):
        eel.SetOrganizedNotes(organized_text)
        speak("Your notes are organized and saved.")

    session = notes.NotesSession(
        on_chunk=lambda text: eel.AppendRawNote(text),
        on_status=lambda status: eel.DisplayMessage(status),
        on_finished=_on_finished,
    )
    _active_notes_session = session
    eel.ShowNotesPanel()
    speak("Sure, go ahead. Say 'stop notes' when you're finished.")
    session.start()


@eel.expose
def requestStopNotes():
    if _active_notes_session:
        _active_notes_session.request_stop()


@eel.expose
def sendTextCommand(text):
    """Handle a typed command and return the reply text so the JS side
    can display it (speak() only produces audio, which isn't visible
    feedback on its own)."""
    text = (text or "").strip()
    if not text:
        return ""

    if brain.is_notes_trigger(text):
        _start_notes_session()
        return "Starting a notes session -- say 'stop notes' when you're done."

    reply = brain.handle_text_command(text)
    if reply:
        speak(reply)
        return reply

    return "Done."


@eel.expose
def setSpeakReplies(enabled):
    global _speak_enabled
    _speak_enabled = bool(enabled)


@eel.expose
def setApiKey(key):
    key = (key or "").strip()
    if key:
        os.environ["ANTHROPIC_API_KEY"] = key
    else:
        os.environ.pop("ANTHROPIC_API_KEY", None)
    return getAiStatus()


@eel.expose
def getAiStatus():
    from engine.ai import is_available
    return is_available()


@eel.expose
def allCommands():
    query = takeCommand()
    print(query)

    if not query:
        eel.ShowHood()
        return

    if brain.is_notes_trigger(query):
        _start_notes_session()
        eel.ShowHood()
        return

    reply = brain.handle_text_command(query)
    if reply:
        speak(reply)

    eel.ShowHood()
