"""Optional pynput-based input backend.

Uses OS-level key event hooks to get real key-down and key-up events,
bypassing terminal character streams and their OS repeat delay.

Requires: pip install pynput
On macOS: grant Accessibility permission on first run.
"""

import time
from threading import Lock

from kbsmash._input import (
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
    KEY_ENTER, KEY_ESCAPE, KEY_SPACE, KEY_BACKSPACE, KEY_TAB,
)


def _load_pynput():
    try:
        from pynput import keyboard
        return keyboard
    except ImportError:
        raise RuntimeError(
            "pynput is not installed. Run: pip install pynput"
        )


def _translate(pynput_keyboard, key):
    Key = pynput_keyboard.Key
    mapping = {
        Key.up: KEY_UP,
        Key.down: KEY_DOWN,
        Key.left: KEY_LEFT,
        Key.right: KEY_RIGHT,
        Key.enter: KEY_ENTER,
        Key.esc: KEY_ESCAPE,
        Key.space: KEY_SPACE,
        Key.backspace: KEY_BACKSPACE,
        Key.tab: KEY_TAB,
    }
    if key in mapping:
        return mapping[key]
    try:
        if key.char is not None:
            return key.char
    except AttributeError:
        pass
    return None


class PynputKeyState:
    """Drop-in replacement for KeyState using real OS key events."""

    def __init__(self, debounce=0):
        self._pynput_keyboard = _load_pynput()
        self._debounce = debounce
        self._down = set()
        self._pending_presses = []
        self._just_pressed = set()
        self._firing = set()
        self._last_fired = {}
        self._lock = Lock()
        self._listener = self._pynput_keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.daemon = True
        self._listener.start()

    def _on_press(self, key):
        name = _translate(self._pynput_keyboard, key)
        if name is None:
            return
        with self._lock:
            if name not in self._down:
                self._pending_presses.append(name)
            self._down.add(name)

    def _on_release(self, key):
        name = _translate(self._pynput_keyboard, key)
        if name is None:
            return
        with self._lock:
            self._down.discard(name)

    def update(self, terminal=None):
        with self._lock:
            self._just_pressed = set(self._pending_presses)
            self._pending_presses.clear()
            currently_down = set(self._down)

        now = time.monotonic()
        self._firing.clear()
        for key in currently_down:
            if self._debounce <= 0:
                self._firing.add(key)
            else:
                last = self._last_fired.get(key)
                if last is None or (now - last) >= self._debounce:
                    self._firing.add(key)
                    self._last_fired[key] = now

        for key in list(self._last_fired):
            if key not in currently_down:
                del self._last_fired[key]

    def is_down(self, key):
        return key in self._firing

    def just_pressed(self, key):
        return key in self._just_pressed

    def keys_down(self):
        return frozenset(self._firing)

    def stop(self):
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
