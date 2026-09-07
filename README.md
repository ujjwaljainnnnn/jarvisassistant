# Jarvis

Jarvis has two front ends that share the same engine (`engine/`):

1. **`main.py`** - the original browser-based "hood" UI (Eel + HTML/CSS/JS
   in `www/`). Click the mic, speak, and Jarvis opens sites/apps and talks
   back.
2. **`jarvis_overlay.py`** - a floating, animated icon that hovers next to
   your mouse cursor at all times. Click it to open a small chat panel
   that answers questions by voice or text, aware of whatever window is
   currently focused - no alt-tabbing, screenshots, or copy-pasting
   context required.

## Setup

```bash
python -m venv envjarvis
source envjarvis/bin/activate   # envjarvis\Scripts\activate on Windows
pip install -r requirements.txt
```

Notes:
- `PyAudio` (needed for the microphone) requires the PortAudio system
  library: `sudo apt install portaudio19-dev` (Linux) or
  `brew install portaudio` (macOS) before `pip install` will build it.
- Text-to-speech uses `pyttsx3`, which needs a system speech engine:
  SAPI5 is built into Windows, macOS uses the built-in `NSSpeechSynthesizer`,
  and Linux needs `espeak`/`espeak-ng` installed.
- On Linux, the overlay's active-window detection uses `xdotool` (or
  `wmctrl` as a fallback) - install one of those for the tutor to know
  what app you're in.

## Running the hood UI

```bash
python main.py
```

Opens `http://localhost:8000` in your default browser. Click the mic
button and speak a command, e.g. "open youtube".

## Running the floating companion / tutor

```bash
python jarvis_overlay.py
```

A small glowing dot appears next to your cursor and follows it around.

- **Left-click + drag**: reposition it (only while cursor-follow is off).
- **Right-click**: toggle whether it follows the cursor or stays put.
- **Double-click**, or use the system tray icon: open/close the chat panel.
- In the chat panel, use **Mic** to ask by voice or type a question
  directly. It shows which window it thinks you're focused on and tailors
  its answer to it (e.g. VS Code, Chrome, Word, Excel, a terminal).

By default it answers from a small built-in knowledge base of tips, so it
works fully offline. To get real, open-ended answers instead of just the
built-in tips, set an API key before launching:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python jarvis_overlay.py
```
