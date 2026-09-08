"""Voice note-taking: say "take notes", ramble as much as you like, say
"stop notes" -- Jarvis turns the raw transcript into clean, organized
notes (via an AI provider when one is configured, see engine.ai,
otherwise a simple offline cleanup) and saves them to disk.
"""

import datetime
import os
import re
import threading

import speech_recognition as sr

from engine import projects
from engine.ai import ask_ai, is_available
from engine.auth import get_current_user
from engine.brain import is_notes_stop
from engine.db import get_client

NOTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notes")

FILLER_WORDS = (
    "umm", "um", "uhh", "uh", "erm", "like", "you know", "i mean",
    "basically", "actually", "sort of", "kind of", "so yeah",
)

ORGANIZE_SYSTEM_PROMPT = (
    "You turn a messy, rambling voice transcript into clear, well-"
    "organized notes. Group related points under short headings, use "
    "bullet points, fix grammar and remove filler words, but do not "
    "invent information that wasn't said. Output plain markdown."
)


def _clean_chunk(chunk):
    text = chunk
    for filler in FILLER_WORDS:
        text = re.sub(rf"\b{re.escape(filler)}\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip(" ,.")
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


def _fallback_organize(chunks):
    heading = f"# Notes - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

    bullets = []
    seen = set()
    for chunk in chunks:
        cleaned = _clean_chunk(chunk)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        bullets.append(f"- {cleaned}")

    if not bullets:
        return heading + "\n\n*(No notes captured.)*"
    return heading + "\n\n" + "\n".join(bullets)


def organize_notes(chunks):
    """Turn the raw speech chunks captured during a notes session into
    clean notes. `chunks` is a list of separately-recognized phrases --
    raw speech has no punctuation, so the natural pause between phrases
    is the best signal for where one thought ends and the next begins."""
    if isinstance(chunks, str):
        chunks = [chunks] if chunks.strip() else []

    if not chunks:
        return f"# Notes - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n*(No notes captured.)*"

    if is_available():
        transcript = "\n".join(chunks)
        organized = ask_ai(ORGANIZE_SYSTEM_PROMPT, transcript)
        if organized:
            return organized

    return _fallback_organize(chunks)


def save_notes(organized_text):
    """Save the organized notes locally (always) and to Supabase (best
    effort -- a network hiccup shouldn't lose a note that's already
    safely on disk)."""
    project = projects.get_current_project()
    subdir = projects.slugify(project["name"]) if project["id"] else ""
    target_dir = os.path.join(NOTES_DIR, subdir) if subdir else NOTES_DIR

    os.makedirs(target_dir, exist_ok=True)
    filename = f"notes_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path = os.path.join(target_dir, filename)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(organized_text)

    user = get_current_user()
    if user:
        try:
            get_client().table("notes").insert(
                {
                    "user_id": user["id"],
                    "project_id": project["id"],
                    "content": organized_text,
                }
            ).execute()
        except Exception as exc:
            print(f"Could not sync note to Supabase (saved locally at {path}): {exc}")

    return path


class NotesSession:
    """Continuously listens on the mic, collecting rambling speech until a
    stop phrase is heard or `request_stop()` is called, then organizes and
    saves it. All callbacks are invoked from background threads."""

    def __init__(self, on_chunk=None, on_status=None, on_finished=None, max_duration=600):
        self.on_chunk = on_chunk
        self.on_status = on_status
        self.on_finished = on_finished
        self.max_duration = max_duration

        self.chunks = []
        self._recognizer = sr.Recognizer()
        self._stop_listening = None
        self._stopped_event = threading.Event()
        self._timeout_timer = None

    def _callback(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio, language="en-in")
        except (sr.UnknownValueError, sr.RequestError):
            return
        if not text:
            return
        if is_notes_stop(text.lower()):
            self.request_stop()
            return
        self.chunks.append(text)
        if self.on_chunk:
            self.on_chunk(text)

    def start(self):
        started_ok = True
        try:
            mic = sr.Microphone()
            with mic as source:
                self._recognizer.adjust_for_ambient_noise(source)
            self._stop_listening = self._recognizer.listen_in_background(
                mic, self._callback, phrase_time_limit=10
            )
        except Exception as exc:
            started_ok = False
            print(f"Microphone error: {exc}")

        if started_ok:
            if self.on_status:
                self.on_status("Listening for notes... say 'stop notes' when done.")
            if self.max_duration:
                self._timeout_timer = threading.Timer(self.max_duration, self.request_stop)
                self._timeout_timer.daemon = True
                self._timeout_timer.start()
        else:
            if self.on_status:
                self.on_status("No microphone available.")
            self._stopped_event.set()

        threading.Thread(target=self._watch, daemon=True).start()

    def is_active(self):
        return not self._stopped_event.is_set()

    def request_stop(self):
        if self._stopped_event.is_set():
            return
        if self._stop_listening:
            self._stop_listening(wait_for_stop=False)
        if self._timeout_timer:
            self._timeout_timer.cancel()
        self._stopped_event.set()

    def _watch(self):
        self._stopped_event.wait()
        if self.on_status:
            self.on_status("Organizing your notes...")
        organized = self.organize()
        path = save_notes(organized)
        if self.on_status:
            self.on_status(f"Notes saved to {path}")
        if self.on_finished:
            self.on_finished(organized, path)

    def raw_text(self):
        return " ".join(self.chunks)

    def organize(self):
        return organize_notes(self.chunks)
