"""Multi-provider AI backend, shared by the tutor Q&A and the notes
organizer. Auto-detects whichever provider's API key is configured
(ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY, checked in that
order) and is fully optional -- everything that uses this degrades to
an offline fallback when no key is configured.
"""

import os

import requests

PROVIDER_ENV_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

PROVIDER_LABELS = {
    "anthropic": "Claude (Anthropic)",
    "openai": "ChatGPT (OpenAI)",
    "gemini": "Gemini (Google)",
}

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = os.environ.get("JARVIS_ANTHROPIC_MODEL", "claude-sonnet-5")

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.environ.get("JARVIS_OPENAI_MODEL", "gpt-4o-mini")

GEMINI_MODEL = os.environ.get("JARVIS_GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def _active_provider():
    """Return the first configured provider's key, in priority order."""
    for provider, env_var in PROVIDER_ENV_VARS.items():
        if os.environ.get(env_var):
            return provider
    return None


def is_available():
    return _active_provider() is not None


def get_status():
    provider = _active_provider()
    if provider:
        return {"enabled": True, "provider": PROVIDER_LABELS[provider]}
    return {"enabled": False, "provider": None}


def _ask_anthropic(system_prompt, user_prompt, max_tokens):
    response = requests.post(
        ANTHROPIC_API_URL,
        headers={
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return "".join(block.get("text", "") for block in data.get("content", []))


def _ask_openai(system_prompt, user_prompt, max_tokens):
    response = requests.post(
        OPENAI_API_URL,
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "content-type": "application/json",
        },
        json={
            "model": OPENAI_MODEL,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _ask_gemini(system_prompt, user_prompt, max_tokens):
    response = requests.post(
        GEMINI_API_URL,
        params={"key": os.environ["GEMINI_API_KEY"]},
        json={
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        return None
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(part.get("text", "") for part in parts)


_PROVIDER_FUNCS = {
    "anthropic": _ask_anthropic,
    "openai": _ask_openai,
    "gemini": _ask_gemini,
}


def ask_ai(system_prompt, user_prompt, max_tokens=600):
    """Return a reply from whichever provider is configured, or None."""
    provider = _active_provider()
    if not provider:
        return None
    try:
        text = _PROVIDER_FUNCS[provider](system_prompt, user_prompt, max_tokens)
        return text.strip() if text else None
    except requests.RequestException as exc:
        print(f"{PROVIDER_LABELS[provider]} request failed: {exc}")
        return None
    except (KeyError, IndexError, ValueError) as exc:
        print(f"{PROVIDER_LABELS[provider]} returned an unexpected response: {exc}")
        return None
