import pyttsx3
import speech_recognition as sr
import eel
import time


def speak(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()



def takeCommand():

    r=sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        eel.DisplayMessage("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source ,10, 6)
    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        query = r.recognize_google(audio, language='en-in') 
        print(f"User said: {query}")
        eel.DisplayMessage(query)
        time.sleep(1.5)
    except Exception as e:
        return ""
        
    return query.lower()

@eel.expose
def allCommands():
    """Listen once, route the spoken command to the right skill, then return to the idle UI."""
    from engine.features import openCommand, tellTime, tellDate, searchGoogle, playYoutube

    query = takeCommand()
    print(query)

    if not query:
        speak("Sorry, I didn't hear anything")
    elif "open" in query:
        openCommand(query)
    elif "time" in query:
        tellTime()
    elif "date" in query or "day is it" in query:
        tellDate()
    elif "youtube" in query or query.startswith("play"):
        playYoutube(query)
    elif "search" in query or "google" in query:
        searchGoogle(query)
    else:
        speak("I can open apps and websites, tell the time or date, search Google, or play YouTube")

    eel.ShowHood()
