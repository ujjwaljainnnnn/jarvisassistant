"""Thin wrapper around the Claude API, shared by the tutor Q&A and the
notes organizer. Fully optional -- everything that uses this degrades to
an offline fallback when no key is configured."""

import os

import requests

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = os.environ.get("JARVIS_MODEL", "claude-sonnet-5")


def is_available():
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def ask_claude(system_prompt, user_prompt, max_tokens=600):
    """Return Claude's reply text, or None if unavailable/failed."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        response = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": DEFAULT_MODEL,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        text = "".join(block.get("text", "") for block in data.get("content", []))
        return text or None
    except requests.RequestException as exc:
        print(f"Claude API request failed: {exc}")
        return None
