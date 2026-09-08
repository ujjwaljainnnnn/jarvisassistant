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

    if _active_notes_session and _active_notes_session.is_active():
        speak("I'm already taking notes -- say 'stop notes' when you're done.")
        return

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
def setPrivateMode(enabled):
    from engine.tutor import set_private_mode
    set_private_mode(enabled)


@eel.expose
def newChat():
    """Clear conversation memory so old context doesn't bleed into a
    fresh topic. The visible transcript is cleared client-side."""
    from engine.tutor import reset_conversation
    reset_conversation()


@eel.expose
def sendTextCommand(text):
    """Handle a typed command. The "you said" bubble is already shown
    optimistically by the caller; this only needs to push Jarvis's side
    of the conversation into the transcript."""
    text = (text or "").strip()
    if not text:
        return

    if brain.is_notes_trigger(text):
        _start_notes_session()
        eel.AppendChatMessage("assistant", "Starting a notes session -- say 'stop notes' when you're done.")
        return

    reply = brain.handle_text_command(text)
    if reply:
        speak(reply)
    eel.AppendChatMessage("assistant", reply or "Done.")


@eel.expose
def setSpeakReplies(enabled):
    global _speak_enabled
    _speak_enabled = bool(enabled)


@eel.expose
def setApiKey(provider, key):
    from engine.ai import PROVIDER_ENV_VARS

    env_var = PROVIDER_ENV_VARS.get(provider)
    key = (key or "").strip()
    if env_var:
        if key:
            os.environ[env_var] = key
        else:
            os.environ.pop(env_var, None)
    return getAiStatus()


@eel.expose
def getAiStatus():
    from engine.ai import get_status
    return get_status()


@eel.expose
def allCommands():
    query = takeCommand()
    print(query)

    if not query:
        eel.ShowHood()
        return

    eel.AppendChatMessage("user", query)

    if brain.is_notes_trigger(query):
        _start_notes_session()
        eel.AppendChatMessage("assistant", "Starting a notes session -- say 'stop notes' when you're done.")
        eel.ShowHood()
        return

    reply = brain.handle_text_command(query)
    if reply:
        speak(reply)
    eel.AppendChatMessage("assistant", reply or "Done.")

    eel.ShowHood()
