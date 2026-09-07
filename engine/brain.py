"""Shared command routing used by both the hood UI and the overlay, so
"open X", "what time is it", note-taking, and general questions are all
understood from either voice or typed text."""

import datetime
import re

from engine.config import ASSISTANT_NAME
from engine.features import openCommand
from engine.tutor import get_response

NOTES_START_PHRASES = (
    "take notes",
    "take a note",
    "start taking notes",
    "start taking a note",
    "start notes",
    "begin taking notes",
    "note this down",
    "take some notes",
)

NOTES_STOP_PHRASES = (
    "stop notes",
    "stop taking notes",
    "that's all",
    "that is all",
    "done with notes",
    "done taking notes",
    "finish notes",
    "end notes",
    "notes done",
    "that's it",
    "stop note",
)

TIME_PHRASES = (
    "what time", "current time", "what's the time", "what is the time", "tell me the time",
)
DATE_PHRASES = (
    "what date", "today's date", "what is the date", "what day is it", "what's the date",
)
NAME_PHRASES = ("your name", "who are you")


def is_notes_trigger(query):
    query = (query or "").lower()
    return any(phrase in query for phrase in NOTES_START_PHRASES)


def is_notes_stop(query):
    query = (query or "").lower()
    return any(phrase in query for phrase in NOTES_STOP_PHRASES)


def handle_text_command(query, window_title=""):
    """Route a non-notes command/question.

    Returns a reply string to speak/show, or None if the handler already
    acted on its own (e.g. "open").
    """
    query = (query or "").strip().lower()
    if not query:
        return "I didn't catch that."

    # Word-boundary match so "opening", "reopen", "open source", etc. --
    # a substring check would wrongly treat those as "open <app>" commands.
    if re.search(r"\bopen\b", query):
        openCommand(query)
        return None

    # Apostrophes vary between typed and voice-recognized text ("what's
    # the time" vs "whats the time"), so compare with them stripped.
    normalized = query.replace("'", "")

    if any(phrase.replace("'", "") in normalized for phrase in TIME_PHRASES):
        return f"It's {datetime.datetime.now().strftime('%I:%M %p')}."

    if any(phrase.replace("'", "") in normalized for phrase in DATE_PHRASES):
        return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."

    if any(phrase in query for phrase in NAME_PHRASES):
        return f"I'm {ASSISTANT_NAME}, your assistant."

    return get_response(query, window_title)
