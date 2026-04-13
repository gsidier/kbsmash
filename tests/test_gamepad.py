"""Tests for the gamepad state tracking.

These tests construct a GamepadState without a real pygame/SDL backend.
Instead of calling __init__, they build an instance manually and drive
the internal state directly (bypassing update() which needs a real
joystick). This verifies the edge-trigger logic, dead-zone, and
normalization without any hardware or display.
"""

from kbsmash._gamepad import (
    GamepadState,
    BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y,
    BUTTON_L1, BUTTON_R1, BUTTON_START, BUTTON_SELECT,
    DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT,
)


def _make_state():
    """Build a GamepadState bypassing __init__ (no real pygame needed)."""
    gp = GamepadState.__new__(GamepadState)
    gp._pygame = None
    gp._deadzone = 0.15
    gp._joystick = None
    gp._buttons = set()
    gp._just_pressed = set()
    gp._axes = {"left": [0.0, 0.0], "right": [0.0, 0.0]}
    gp._triggers = {"left": 0.0, "right": 0.0}
    return gp


def _simulate_frame(gp, buttons=None, axes=None, triggers=None):
    """Simulate what update() does: set held buttons and compute edges.

    This replaces the real update() which needs pygame event.pump().
    """
    prev = set(gp._buttons)
    gp._buttons = set(buttons or [])
    gp._just_pressed = gp._buttons - prev
    if axes:
        for which, vals in axes.items():
            gp._axes[which] = list(vals)
    if triggers:
        for which, val in triggers.items():
            gp._triggers[which] = val


# --- Buttons ---

def test_button_press_edge_and_held():
    gp = _make_state()
    _simulate_frame(gp, buttons=[BUTTON_A])
    assert gp.button_pressed(BUTTON_A)
    assert gp.button_down(BUTTON_A)
    # Next frame: still held, edge clears
    _simulate_frame(gp, buttons=[BUTTON_A])
    assert not gp.button_pressed(BUTTON_A)
    assert gp.button_down(BUTTON_A)


def test_button_release():
    gp = _make_state()
    _simulate_frame(gp, buttons=[BUTTON_A])
    assert gp.button_down(BUTTON_A)
    _simulate_frame(gp, buttons=[])
    assert not gp.button_down(BUTTON_A)


def test_multiple_buttons():
    gp = _make_state()
    _simulate_frame(gp, buttons=[BUTTON_A, BUTTON_B])
    assert gp.button_down(BUTTON_A)
    assert gp.button_down(BUTTON_B)
    assert gp.button_pressed(BUTTON_A)
    assert gp.button_pressed(BUTTON_B)


def test_buttons_down_returns_frozenset():
    gp = _make_state()
    _simulate_frame(gp, buttons=[BUTTON_A, BUTTON_L1])
    assert gp.buttons_down() == frozenset({BUTTON_A, BUTTON_L1})


def test_all_face_buttons():
    gp = _make_state()
    for btn in [BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y]:
        _simulate_frame(gp, buttons=[btn])
        assert gp.button_down(btn)
        _simulate_frame(gp, buttons=[])
        assert not gp.button_down(btn)


def test_shoulder_and_menu():
    gp = _make_state()
    for btn in [BUTTON_L1, BUTTON_R1, BUTTON_START, BUTTON_SELECT]:
        _simulate_frame(gp, buttons=[btn])
        assert gp.button_down(btn)


def test_no_buttons_initially():
    gp = _make_state()
    assert gp.buttons_down() == frozenset()
    assert not gp.button_down(BUTTON_A)
    assert not gp.button_pressed(BUTTON_A)


# --- D-pad ---

def test_dpad_press_and_release():
    gp = _make_state()
    _simulate_frame(gp, buttons=[DPAD_UP])
    assert gp.button_down(DPAD_UP)
    assert gp.button_pressed(DPAD_UP)
    _simulate_frame(gp, buttons=[])
    assert not gp.button_down(DPAD_UP)


def test_dpad_direction_change():
    gp = _make_state()
    _simulate_frame(gp, buttons=[DPAD_LEFT])
    assert gp.button_down(DPAD_LEFT)
    _simulate_frame(gp, buttons=[DPAD_RIGHT])
    assert gp.button_down(DPAD_RIGHT)
    assert not gp.button_down(DPAD_LEFT)
    assert gp.button_pressed(DPAD_RIGHT)


def test_dpad_diagonal():
    gp = _make_state()
    _simulate_frame(gp, buttons=[DPAD_UP, DPAD_RIGHT])
    assert gp.button_down(DPAD_UP)
    assert gp.button_down(DPAD_RIGHT)


# --- Analog sticks ---

def test_stick_values():
    gp = _make_state()
    _simulate_frame(gp, axes={"left": [0.75, -0.5]})
    x, y = gp.stick("left")
    assert x == 0.75
    assert y == -0.5


def test_stick_default_zero():
    gp = _make_state()
    x, y = gp.stick("left")
    assert x == 0.0
    assert y == 0.0


def test_right_stick_independent():
    gp = _make_state()
    _simulate_frame(gp, axes={"left": [1.0, 0.0], "right": [-1.0, 0.5]})
    lx, ly = gp.stick("left")
    rx, ry = gp.stick("right")
    assert lx == 1.0
    assert rx == -1.0
    assert ry == 0.5


# --- Triggers ---

def test_trigger_values():
    gp = _make_state()
    _simulate_frame(gp, triggers={"left": 0.8, "right": 0.0})
    assert gp.trigger("left") == 0.8
    assert gp.trigger("right") == 0.0


def test_trigger_default_zero():
    gp = _make_state()
    assert gp.trigger("left") == 0.0
    assert gp.trigger("right") == 0.0


def test_trigger_full():
    gp = _make_state()
    _simulate_frame(gp, triggers={"left": 1.0, "right": 1.0})
    assert gp.trigger("left") == 1.0
    assert gp.trigger("right") == 1.0
