"""Optional gamepad input backend.

Uses the `inputs` library (USB HID gamepads on Win/Mac/Linux). Runs a
background polling thread and exposes the same edge/held semantics as
`KeyState`, plus analog sticks and triggers.

Requires: `uv sync --extra gamepad`
"""

import threading
import time


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


# inputs-library code -> our public name
_BUTTON_MAP = {
    "BTN_SOUTH": BUTTON_A,
    "BTN_EAST": BUTTON_B,
    "BTN_WEST": BUTTON_X,
    "BTN_NORTH": BUTTON_Y,
    "BTN_TL": BUTTON_L1,
    "BTN_TR": BUTTON_R1,
    "BTN_SELECT": BUTTON_SELECT,
    "BTN_START": BUTTON_START,
    "BTN_MODE": BUTTON_HOME,
    "BTN_THUMBL": BUTTON_L3,
    "BTN_THUMBR": BUTTON_R3,
    # Some controllers report dpad as discrete buttons:
    "BTN_DPAD_UP": DPAD_UP,
    "BTN_DPAD_DOWN": DPAD_DOWN,
    "BTN_DPAD_LEFT": DPAD_LEFT,
    "BTN_DPAD_RIGHT": DPAD_RIGHT,
}


def _load_inputs():
    try:
        import inputs
        return inputs
    except ImportError:
        raise RuntimeError(
            "inputs is not installed. Run: uv sync --extra gamepad"
        )


class GamepadState:
    """Tracks button/axis state from a gamepad, queried per-frame.

    Events are drained in a background thread; call `update()` once per
    frame to snapshot edge-triggered presses. Held state and analog values
    can be queried any time and always reflect the latest events.

    Parameters:
        deadzone: analog stick magnitude below which the axis is zeroed
        stick_range: raw max value the device reports on sticks. Most
            modern XInput/Linux evdev devices report int16 (32767); some
            use 1023 or 255. Auto-detected on first event if not set.
    """

    def __init__(self, deadzone=0.15, stick_range=32767.0):
        self._inputs = _load_inputs()
        self._deadzone = deadzone
        self._stick_range = float(stick_range)
        self._buttons = set()
        self._pending_presses = []
        self._just_pressed = set()
        self._axes = {
            "left":  [0.0, 0.0],
            "right": [0.0, 0.0],
        }
        self._triggers = {"left": 0.0, "right": 0.0}
        self._hat = [0, 0]  # (x, y), -1/0/1
        self._lock = threading.Lock()
        self._stopped = False
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    # ---- Background polling ----

    def _poll(self):
        while not self._stopped:
            try:
                events = self._inputs.get_gamepad()
            except Exception:
                # No gamepad connected, or transient read error. Back off
                # so the thread doesn't busy-loop, then retry — this makes
                # hot-plugging work transparently.
                time.sleep(0.5)
                continue
            for event in events:
                self._handle_event(event)

    def _handle_event(self, event):
        if event.ev_type == "Key":
            self._handle_button(event.code, event.state)
        elif event.ev_type == "Absolute":
            self._handle_axis(event.code, event.state)

    def _handle_button(self, code, state):
        name = _BUTTON_MAP.get(code)
        if name is None:
            return
        with self._lock:
            if state:
                if name not in self._buttons:
                    self._pending_presses.append(name)
                self._buttons.add(name)
            else:
                self._buttons.discard(name)

    def _handle_axis(self, code, raw):
        # Analog sticks
        if code == "ABS_X":
            self._set_stick("left", 0, raw)
        elif code == "ABS_Y":
            self._set_stick("left", 1, raw)
        elif code == "ABS_RX":
            self._set_stick("right", 0, raw)
        elif code == "ABS_RY":
            self._set_stick("right", 1, raw)
        # Triggers (0..255 typically; normalize to 0..1)
        elif code == "ABS_Z":
            with self._lock:
                self._triggers["left"] = max(0.0, min(1.0, raw / 255.0))
        elif code == "ABS_RZ":
            with self._lock:
                self._triggers["right"] = max(0.0, min(1.0, raw / 255.0))
        # Hat / dpad as axes
        elif code == "ABS_HAT0X":
            self._set_hat(0, raw)
        elif code == "ABS_HAT0Y":
            self._set_hat(1, raw)

    def _set_stick(self, which, axis_idx, raw):
        val = raw / self._stick_range
        if val > 1.0:
            val = 1.0
        elif val < -1.0:
            val = -1.0
        if abs(val) < self._deadzone:
            val = 0.0
        with self._lock:
            self._axes[which][axis_idx] = val

    def _set_hat(self, axis_idx, raw):
        # raw is -1, 0, or +1 on evdev hat axes
        with self._lock:
            self._hat[axis_idx] = raw
            if axis_idx == 0:
                neg, pos = DPAD_LEFT, DPAD_RIGHT
            else:
                neg, pos = DPAD_UP, DPAD_DOWN
            # Release both, then press the active one (if any)
            released_neg = neg in self._buttons
            released_pos = pos in self._buttons
            self._buttons.discard(neg)
            self._buttons.discard(pos)
            if raw < 0:
                self._buttons.add(neg)
                if not released_neg:
                    self._pending_presses.append(neg)
            elif raw > 0:
                self._buttons.add(pos)
                if not released_pos:
                    self._pending_presses.append(pos)

    # ---- Per-frame snapshot + queries ----

    def update(self):
        """Snapshot edge-triggered presses for this frame."""
        with self._lock:
            self._just_pressed = set(self._pending_presses)
            self._pending_presses.clear()

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
        with self._lock:
            x, y = self._axes[which]
            return (x, y)

    def trigger(self, which):
        """Return trigger pressure in [0, 1] for 'left' or 'right'."""
        with self._lock:
            return self._triggers[which]

    def stop(self):
        self._stopped = True
