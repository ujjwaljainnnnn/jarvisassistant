# Jarvis

Jarvis has two front ends that share the same engine (`engine/`):

1. **`main.py`** - the browser-based "hood" UI (Eel + HTML/CSS/JS in
   `www/`). Click the mic (or type), and Jarvis opens sites/apps, answers
   questions, and takes voice notes for you.
2. **`jarvis_overlay.py`** - a floating, animated icon that hovers next to
   your mouse cursor at all times. Click it to open a small chat panel
   that answers questions by voice or text, aware of whatever window is
   currently focused - no alt-tabbing, screenshots, or copy-pasting
   context required.

Both front ends share one account system (sign up once, and you're
recognized on both) and the same "take notes" feature.

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
- Accounts are stored locally in SQLite (Python's built-in `sqlite3`, no
  extra install) under your OS's per-user app-data folder, e.g.
  `%APPDATA%\Jarvis` on Windows, `~/Library/Application Support/Jarvis`
  on macOS, `~/.local/share/Jarvis` on Linux. Passwords are hashed
  (PBKDF2-HMAC-SHA256, random per-user salt) and never stored in plain
  text. This is a local single-machine account store for a personalized,
  "remember me" experience - not a network auth service.

## Accounts

The first time you launch either front end, you'll see a **Log in /
Sign up** screen. Create an account with a name, email, and password
(6+ characters). After that, Jarvis remembers you across restarts of
both `main.py` and `jarvis_overlay.py` - no need to log in every time.
Log out from the hood UI's Settings panel, or the overlay's tray menu.

## Running the hood UI

```bash
python main.py
```

Opens `http://localhost:8000` in your default browser.

- **Mic button**: speak a command, e.g. "open youtube", "what time is
  it", or "take notes".
- **Chat box + send button**: type the same kinds of commands instead of
  speaking them; press Enter to send.
- **Settings (gear icon)**: toggle spoken replies, set an API key for
  smarter answers, or log out.

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
- The tray icon also has a **Take notes** shortcut.

By default it answers from a small built-in knowledge base of tips, so it
works fully offline. To get real, open-ended answers instead of just the
built-in tips, set an API key before launching:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python jarvis_overlay.py
```

## Taking notes

Say (or type) **"take notes"** in either front end. Jarvis opens a side
notes panel and starts listening continuously - just talk normally,
including all the "um"s, tangents, and backtracking. Say **"stop
notes"** (or click **Stop & Organize**) when you're done.

Jarvis then turns your rambling into clean, organized notes:
- With `ANTHROPIC_API_KEY` set, Claude groups your points into headings
  and bullets, fixes grammar, and removes filler - without inventing
  anything you didn't say.
- Without an API key, an offline fallback still strips filler words,
  de-duplicates repeated points, and turns each thing you said into a
  clean bullet point.

Notes are saved as markdown files under `notes/` in the project folder
(git-ignored), timestamped like `notes_20260907_143000.md`.
