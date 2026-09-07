import time

import eel

from engine.speech import speak as _speak, listen as _listen


def speak(text):
    _speak(text, on_speak=eel.DisplayMessage)


def takeCommand():
    print("Listening...")
    query = _listen(on_status=eel.DisplayMessage)
    if query:
        print(f"User said: {query}")
        time.sleep(1.5)
    return query


@eel.expose
def allCommands():
    query = takeCommand()
    print(query)

    if "open" in query:
        from engine.features import openCommand
        openCommand(query)
    elif query:
        speak("Sorry, I don't know how to do that yet.")

    eel.ShowHood()
