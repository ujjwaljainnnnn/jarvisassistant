# Jarvis: Desktop Voice Assistant

> A Python voice assistant with an animated web UI. Click the mic, speak, and Jarvis listens, understands the command, answers out loud and acts on it.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python) ![Eel](https://img.shields.io/badge/Eel-Python%E2%86%94JS%20bridge-orange) ![SpeechRecognition](https://img.shields.io/badge/SpeechRecognition-Google%20STT-4285F4) ![pyttsx3](https://img.shields.io/badge/pyttsx3-offline%20TTS-green)

## What it can do

| Say… | Jarvis… |
|---|---|
| "Open YouTube" / "Open GitHub" | opens the website in your browser |
| "Open notepad" | launches the local app (Windows) |
| "What's the time?" / "What's the date?" | answers out loud |
| "Search Google for RIT Dubai" | runs a Google search |
| "Play lo-fi music on YouTube" | opens YouTube results for it |

## How it works

```
 ┌──────────── Frontend (www/) ─────────────┐        ┌────────── Backend (engine/) ──────────┐
 │ HTML/CSS/JS · Bootstrap · Textillate      │  Eel   │ command.py                            │
 │ animated "hood" + Siri-style wave UI      │◀──────▶│  takeCommand() → mic → Google STT     │
 │ mic button → eel.allCommands()            │        │  allCommands() → intent routing       │
 │ eel.expose(DisplayMessage / ShowHood)     │        │  speak() → pyttsx3 text-to-speech     │
 └───────────────────────────────────────────┘        │ features.py → open / time / search …  │
                                                      └───────────────────────────────────────┘
```

- **Two-way bridge:** [Eel](https://github.com/python-eel/Eel) exposes Python functions to JavaScript (`eel.allCommands()`), and JS functions to Python (`eel.DisplayMessage()` shows live captions while Jarvis listens and speaks).
- **Speech-to-text:** `speech_recognition` with ambient-noise calibration and a pause threshold, using Google's recognizer (`en-IN`).
- **Text-to-speech:** `pyttsx3` (offline, SAPI5 voice on Windows).
- **Intent routing:** keyword-based dispatcher in `allCommands()` maps the transcript to a skill in `features.py`.

## Run it (Windows)

```bash
git clone https://github.com/ujjwaljainnnnn/jarvisassistant.git
cd jarvisassistant
python -m venv envjarvis
envjarvis\Scripts\activate
pip install -r requirements.txt
python main.py
```

The app opens in an Edge app window at `http://localhost:8000`. A microphone and an internet connection (for speech recognition) are required.

## Roadmap

- [ ] Wake-word detection ("Hey Jarvis") instead of a button
- [ ] LLM intent parsing instead of keyword matching
- [ ] WhatsApp messaging and contacts
- [ ] Cross-platform app launching (macOS/Linux)

## Author

**Ujjwal Jain**, Computing & IT, RIT Dubai · [GitHub](https://github.com/ujjwaljainnnnn)
