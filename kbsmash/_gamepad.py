"""Optional gamepad input backend.

Uses pygame's joystick API (backed by SDL2) which has robust cross-platform
support including Bluetooth Xbox/PlayStation controllers on macOS, evdev on
Linux, and XInput on Windows.

Polling is synchronous — call `update()` once per frame from the main thread.
No background thread is needed because SDL2 buffers events internally.

Requires: `uv sync --extra gamepad`
"""

import os


# --- Public constants ---

BUTTON_A = "BUTTON_A"
BUTTON_B = "BUTTON_B"
BUTTON_X = "BUTTON_X"
BUTTON_Y = "BUTTON_Y"
BUTTON_L1 = "BUTTON_L1"
BUTTON_R1 = "BUTTON_R1"
BUTTON_L3 = "BUTTON_L3"   # left stick click
BUTTON_R3 = "BUTTON_R3"   # right stick click
BUTTON_START = "BUTTON_START"
BUTTON_SELECT = "BUTTON_SELECT"
BUTTON_HOME = "BUTTON_HOME"
DPAD_UP = "DPAD_UP"
DPAD_DOWN = "DPAD_DOWN"
DPAD_LEFT = "DPAD_LEFT"
DPAD_RIGHT = "DPAD_RIGHT"

STICK_LEFT = "left"
STICK_RIGHT = "right"
TRIGGER_LEFT = "left"
TRIGGER_RIGHT = "right"

# SDL GameController button indices (standard mapping for recognized pads)
_BUTTON_MAP = {
    0: BUTTON_A,
    1: BUTTON_B,
    2: BUTTON_X,
    3: BUTTON_Y,
    4: BUTTON_SELECT,
    5: BUTTON_HOME,
    6: BUTTON_START,
    7: BUTTON_L3,
    8: BUTTON_R3,
    9: BUTTON_L1,
    10: BUTTON_R1,
    11: DPAD_UP,
    12: DPAD_DOWN,
    13: DPAD_LEFT,
    14: DPAD_RIGHT,
}


def _init_pygame():
    """Import and initialize pygame for headless joystick-only use."""
    # Prevent SDL from opening a real window or audio device.
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    # Suppress "pygame X.X.X" banner on import.
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    try:
        import pygame
    except ImportError:
        raise RuntimeError(
            "pygame is not installed. Run: uv sync --extra gamepad"
        )
    pygame.display.init()
    pygame.joystick.init()
    return pygame


class GamepadState:
    """Tracks button/axis state from the first connected gamepad.

    Call `update()` once per frame (from the main thread) to pump SDL events,
    read the current joystick state, and snapshot edge-triggered presses.

    Parameters:
        deadzone: analog stick magnitude below which the axis reads as 0.
    """

    def __init__(self, deadzone=0.15):
        self._pygame = _init_pygame()
        self._deadzone = deadzone
        self._joystick = None
        self._buttons = set()
        self._just_pressed = set()
        self._axes = {"left": [0.0, 0.0], "right": [0.0, 0.0]}
        self._triggers = {"left": 0.0, "right": 0.0}

    def update(self):
        """Pump SDL events, read gamepad state, compute edge presses."""
        self._pygame.event.pump()

        # Hot-plug: try to grab the first joystick if we don't have one yet.
        if self._joystick is None:
            if self._pygame.joystick.get_count() > 0:
                self._joystick = self._pygame.joystick.Joystick(0)
                self._joystick.init()
        if self._joystick is None:
            self._just_pressed = set()
            return

        prev = set(self._buttons)
        self._buttons.clear()

        # --- Buttons ---
        num_buttons = self._joystick.get_numbuttons()
        for idx, name in _BUTTON_MAP.items():
            if idx < num_buttons and self._joystick.get_button(idx):
                self._buttons.add(name)

        # --- D-pad via hat (some controllers report dpad as a hat) ---
        if self._joystick.get_numhats() > 0:
            hx, hy = self._joystick.get_hat(0)
            if hx < 0: self._buttons.add(DPAD_LEFT)
            if hx > 0: self._buttons.add(DPAD_RIGHT)
            # SDL hat: y +1 = up, -1 = down
            if hy > 0: self._buttons.add(DPAD_UP)
            if hy < 0: self._buttons.add(DPAD_DOWN)

        self._just_pressed = self._buttons - prev

        # --- Analog sticks (axes 0-3) ---
        def _axis(idx):
            if idx < self._joystick.get_numaxes():
                v = self._joystick.get_axis(idx)
                return 0.0 if abs(v) < self._deadzone else v
            return 0.0

        self._axes["left"]  = [_axis(0), _axis(1)]
        self._axes["right"] = [_axis(2), _axis(3)]

        # --- Triggers (axes 4-5): SDL reports -1..1, normalize to 0..1 ---
        def _trigger(idx):
            if idx < self._joystick.get_numaxes():
                return (self._joystick.get_axis(idx) + 1.0) / 2.0
            return 0.0

        self._triggers["left"]  = _trigger(4)
        self._triggers["right"] = _trigger(5)

    def button_down(self, button):
        return button in self._buttons

    def button_pressed(self, button):
        return button in self._just_pressed

    def buttons_down(self):
        return frozenset(self._buttons)

    def stick(self, which):
        """Return (x, y) for the left or right analog stick, in [-1, 1].

        y is positive-down (matching screen coordinates).
        """
        x, y = self._axes[which]
        return (x, y)

    def trigger(self, which):
        """Return trigger pressure in [0, 1] for 'left' or 'right'."""
        return self._triggers[which]

    def stop(self):
        if self._joystick is not None:
            self._joystick.quit()
            self._joystick = None
        self._pygame.joystick.quit()
        self._pygame.display.quit()
