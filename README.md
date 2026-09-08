# Jarvis

Jarvis has two front ends that share the same engine (`engine/`):

1. **`main.py`** - the browser-based "hood" UI (Eel + HTML/CSS/JS in
   `www/`). Click the mic (or type), and Jarvis opens sites/apps, answers
   questions, takes voice notes, and keeps a real chat transcript.
2. **`jarvis_overlay.py`** - a floating, animated icon that hovers next to
   your mouse cursor at all times. Click it to open a small chat panel
   that answers questions by voice or text, aware of whatever window is
   currently focused - no alt-tabbing, screenshots, or copy-pasting
   context required.

Both front ends share one account system (sign up once, and you're
recognized on both), the same **Projects** (separate named workspaces),
and the same **"take notes"** feature.

## Setup

```bash
python -m venv envjarvis
source envjarvis/bin/activate   # envjarvis\Scripts\activate on Windows
pip install -r requirements.txt
```

Then set up Supabase (below) -- Jarvis needs it to run at all.

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

## Supabase setup

Jarvis's accounts, projects, and notes are stored in Supabase (a hosted
Postgres database with built-in auth) rather than locally, so logging in
requires internet access. This takes about five minutes, once:

1. **Create a project.** Go to [supabase.com](https://supabase.com),
   create a free account, and create a new project.
2. **Apply the schema.** Open your project's SQL Editor, paste in the
   contents of [`supabase/schema.sql`](supabase/schema.sql) from this
   repo, and run it. This creates the `projects` and `notes` tables with
   row-level security already enabled, so each account can only ever see
   its own data.
3. **Get your API keys.** In your project's Settings -> API, copy the
   **Project URL** and the **anon / public key** (the legacy JWT-style
   `anon` key or the newer `sb_publishable_...` key both work - never
   use the **service_role** key here, that one's secret and this app
   never needs it).
4. **Set the environment variables** before launching either front end:

   ```bash
   export SUPABASE_URL="https://<your-project-ref>.supabase.co"
   export SUPABASE_ANON_KEY="<your anon/publishable key>"
   ```

   (On Windows: `set SUPABASE_URL=...` / `set SUPABASE_ANON_KEY=...`, or
   add them as environment variables in VS Code's launch config.)

5. **Optional convenience tweak:** by default, Supabase requires
   confirming your email before you can log in after signing up. For a
   personal local app this is often unnecessary friction - you can turn
   it off in your project's Authentication -> Sign In / Providers ->
   Email settings ("Confirm email").

Without these two environment variables set, `main.py` and
`jarvis_overlay.py` will print a clear error and refuse to start, rather
than failing partway through.

## Accounts

The first time you launch either front end, you'll see a **Log in /
Sign up** screen backed by Supabase Auth. Create an account with a name,
email, and password (6+ characters). After that, Jarvis remembers you
across restarts of both `main.py` and `jarvis_overlay.py` - no need to
log in every time. Log out from the hood UI's Settings panel, or the
overlay's tray menu.

## Projects

Click the project pill next to the Jarvis logo (top-left) to see your
projects, switch between them, or create a new one. Each project keeps
its own chat memory and its own notes folder (`notes/<project-name>/`),
so "the novel I'm writing" and "my tax questions" don't bleed into each
other. There's always a default **General** project you don't need to
create.

## Connecting a real AI

Without any setup, both front ends answer from a small offline
knowledge base (app shortcuts, time/date, opening sites) and a rule-
based note cleanup. To get real, open-ended answers and genuinely
AI-organized notes, connect any one of these -- Jarvis auto-detects
whichever is present, checked in this order:

| Provider | Where to get a key | Env var |
|---|---|---|
| Claude (Anthropic) | console.anthropic.com | `ANTHROPIC_API_KEY` |
| ChatGPT (OpenAI) | platform.openai.com | `OPENAI_API_KEY` |
| Gemini (Google) | aistudio.google.com | `GEMINI_API_KEY` |

Easiest: open the hood UI's **Settings** (gear icon), pick a provider,
and paste the key -- it's kept in memory for that run only, never
written to disk. Or export the matching env var before launching
either front end. Only paste a key somewhere you trust; this app never
sends it anywhere but the provider you picked.

## Running the hood UI

```bash
python main.py
```

Opens `http://localhost:8000` in your default browser.

- **Mic button**: speak a command, e.g. "open youtube", "what time is
  it", or "take notes".
- **Chat box + send button**: type the same kinds of commands instead of
  speaking them; press Enter to send. Every exchange (voice or typed)
  shows up in a real, scrolling chat transcript, with memory of what
  you've asked so far in the current project.
- **Ghost icon (private mode)**: answers in a fully temporary,
  context-free way and nothing from it is remembered afterward -- like
  ChatGPT's "temporary chat."
- **Pencil icon (new chat)**: clears the current project's conversation
  memory and transcript.
- **Project pill** (top-left): switch projects or create a new one.
- **Settings (gear icon)**: toggle spoken replies, connect a Claude,
  ChatGPT, or Gemini API key for smarter answers, or log out.

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
- The tray icon also has a **Take notes** shortcut and a **Log out**.

By default it answers from a small built-in knowledge base of tips, so
answering doesn't require internet beyond the Supabase login itself. To
get real, open-ended answers instead of just the built-in tips, set one
of these before launching (whichever you have -- Jarvis auto-detects it):

```bash
export ANTHROPIC_API_KEY=sk-ant-...     # Claude
# or
export OPENAI_API_KEY=sk-...            # ChatGPT
# or
export GEMINI_API_KEY=...               # Gemini

python jarvis_overlay.py
```

## Taking notes

Say (or type) **"take notes"** in either front end. Jarvis opens a side
notes panel and starts listening continuously - just talk normally,
including all the "um"s, tangents, and backtracking. Say **"stop
notes"** (or click **Stop & Organize**) when you're done.

Jarvis then turns your rambling into clean, organized notes:
- With an AI provider connected (Settings, or an env var -- see above),
  it groups your points into headings and bullets, fixes grammar, and
  removes filler - without inventing anything you didn't say.
- Without one, an offline fallback still strips filler words,
  de-duplicates repeated points, and turns each thing you said into a
  clean bullet point.

Notes are saved as markdown files under `notes/` (or `notes/<project
name>/` if you're inside a project) in the project folder (git-ignored),
timestamped like `notes_20260907_143000.md`, and also synced to your
Supabase `notes` table for safekeeping.
