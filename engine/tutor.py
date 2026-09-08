"""The "brain" behind the floating overlay's chat / tutor panel.

Works fully offline out of the box with a small rule-based knowledge base
of tips for common apps and general commands. If an API key is configured
for Claude, ChatGPT, or Gemini (see engine.ai), questions that the
rule-based layer can't answer are instead sent to that model, along with
the active window title as context, so the assistant can give real,
situation-aware answers.
"""

from engine.ai import ask_ai

# Rolling memory of the LLM conversation so follow-up questions ("what
# about the other one?") work instead of every question being answered
# in isolation. Rule-based tips are stateless one-liners and deliberately
# don't participate in this -- only real model turns need continuity.
_conversation_history = []
MAX_HISTORY_MESSAGES = 12  # 6 user/assistant exchanges

# Private mode (like ChatGPT's "temporary chat"): while on, a turn uses no
# prior context and is never added to memory afterward -- fully isolated,
# not just hidden from the transcript.
_private_mode = False


def reset_conversation():
    """Start a fresh conversation -- called by "New chat" and on logout."""
    _conversation_history.clear()


def set_private_mode(enabled):
    global _private_mode
    _private_mode = bool(enabled)


def is_private_mode():
    return _private_mode


# Lightweight, offline "how do I..." tips keyed by (substring of window
# title -> substring of query -> answer). Checked before falling back to
# an LLM call, so the assistant is still useful with zero configuration.
APP_TIPS = {
    "visual studio code": {
        "command palette": "Press Ctrl+Shift+P (Cmd+Shift+P on Mac) to open the Command Palette.",
        "terminal": "Press Ctrl+` to toggle the integrated terminal.",
        "find": "Press Ctrl+F to find, or Ctrl+Shift+F to search across the whole project.",
        "format": "Press Shift+Alt+F to format the current file.",
    },
    "chrome": {
        "tab": "Ctrl+T opens a new tab, Ctrl+Shift+T reopens the last closed tab.",
        "search": "Type your query directly in the address bar to search.",
        "incognito": "Ctrl+Shift+N opens an Incognito window.",
    },
    "word": {
        "bold": "Ctrl+B makes selected text bold.",
        "save": "Ctrl+S saves the document.",
    },
    "excel": {
        "sum": "Use =SUM(range) to add up a range of cells, e.g. =SUM(A1:A10).",
        "filter": "Select your data and press Ctrl+Shift+L to toggle AutoFilter.",
    },
    "terminal": {
        "list": "Use `ls` (or `dir` on Windows) to list files in the current directory.",
        "clear": "Type `clear` (or `cls` on Windows) to clear the terminal.",
    },
}

GENERAL_TIPS = {
    "copy": "Ctrl+C copies the current selection.",
    "paste": "Ctrl+V pastes from the clipboard.",
    "undo": "Ctrl+Z undoes the last action.",
    "screenshot": "Windows: Win+Shift+S. macOS: Cmd+Shift+4. Linux: PrtScn (varies by desktop).",
}


def _rule_based_answer(query, window_title):
    query = query.lower()
    window_title = (window_title or "").lower()

    for app_name, tips in APP_TIPS.items():
        if app_name in window_title:
            for keyword, answer in tips.items():
                if keyword in query:
                    return answer

    for keyword, answer in GENERAL_TIPS.items():
        if keyword in query:
            return answer

    return None


def _llm_answer(query, window_title):
    system_prompt = (
        "You are Jarvis, a concise on-screen desktop tutor. The user is "
        f"currently focused on this window: '{window_title or 'unknown'}'. "
        "Give short, practical, actionable answers (2-4 sentences), as if "
        "guiding them live while they work."
    )
    history = [] if _private_mode else _conversation_history
    reply = ask_ai(system_prompt, query, max_tokens=300, history=history)
    if reply and not _private_mode:
        _conversation_history.append({"role": "user", "content": query})
        _conversation_history.append({"role": "assistant", "content": reply})
        del _conversation_history[:-MAX_HISTORY_MESSAGES]
    return reply


def get_response(query, window_title=""):
    """Return a tutor reply for `query`, given the active window title."""
    if not query:
        return "I didn't catch a question -- try again?"

    answer = _rule_based_answer(query, window_title)
    if answer:
        return answer

    answer = _llm_answer(query, window_title)
    if answer:
        return answer

    return (
        "I don't have a built-in answer for that yet. Add a Claude, "
        "ChatGPT, or Gemini API key in Settings to let me look up a "
        "real answer."
    )
