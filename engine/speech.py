"""Cross-platform text-to-speech and speech-recognition helpers.

Shared by both the browser-based hood UI (engine.command) and the
floating overlay assistant so voice handling only lives in one place.
"""

import pyttsx3
import speech_recognition as sr

_tts_engine = None


def _get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        # No driver name -> pyttsx3 auto-picks sapi5 / nsss / espeak per OS.
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 174)
        _tts_engine = engine
    return _tts_engine


def speak(text, on_speak=None):
    """Speak `text` aloud, optionally reporting it to `on_speak(text)` first."""
    if on_speak:
        on_speak(text)
    try:
        engine = _get_tts_engine()
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"Text-to-speech unavailable: {exc}")


def listen(timeout=10, phrase_time_limit=6, on_status=None):
    """Listen on the default microphone and return the recognized text
    (lowercased), or "" if nothing usable was heard."""
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            if on_status:
                on_status("Listening...")
            recognizer.pause_threshold = 1
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        if on_status:
            on_status("Didn't hear anything.")
        return ""
    except Exception as exc:
        # Covers OSError ("no default input device") as well as PyAudio
        # being missing entirely (raised as AttributeError by speech_recognition).
        if on_status:
            on_status("No microphone available.")
        print(f"Microphone error: {exc}")
        return ""

    try:
        if on_status:
            on_status("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        if on_status:
            on_status(query)
        return query.lower()
    except sr.UnknownValueError:
        if on_status:
            on_status("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as exc:
        if on_status:
            on_status("Speech recognition service unavailable.")
        print(f"Speech recognition request failed: {exc}")
        return ""
