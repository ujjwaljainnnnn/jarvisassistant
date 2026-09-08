"""Cross-platform lookup of the title of the currently focused window.

This is how the overlay assistant "observes" what you're doing without
needing screenshots: it just asks the OS which window has focus, so the
tutor brain can react to context (e.g. "I see you're in VS Code").
"""

import platform
import subprocess

_SYSTEM = platform.system()


def get_active_window_title():
    """Return the title of the foreground window, or "" if unavailable."""
    try:
        if _SYSTEM == "Windows":
            return _windows_active_window()
        if _SYSTEM == "Darwin":
            return _macos_active_window()
        return _linux_active_window()
    except Exception:
        return ""


def _windows_active_window():
    import ctypes

    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def _macos_active_window():
    script = (
        'tell application "System Events" to get name of first process '
        'whose frontmost is true'
    )
    result = subprocess.run(
        ["osascript", "-e", script], capture_output=True, text=True, timeout=2
    )
    return result.stdout.strip()


def _linux_active_window():
    # Try xdotool first, then fall back to wmctrl.
    try:
        result = subprocess.run(
            ["xdotool", "getactivewindow", "getwindowname"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass

    try:
        result = subprocess.run(
            ["wmctrl", "-l"], capture_output=True, text=True, timeout=2
        )
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if lines:
            # wmctrl -l doesn't mark the focused window; best effort: last one.
            return lines[-1].split(None, 3)[-1]
    except FileNotFoundError:
        pass

    return ""
