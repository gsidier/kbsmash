import curses
import time

import pytest

from kbsmash._input import (
    translate_key, KeyState,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
    KEY_ENTER, KEY_ESCAPE, KEY_SPACE, KEY_TAB, KEY_BACKSPACE,
)
from conftest import FakeTerminal


# --- translate_key ---

def test_translate_key_none():
    assert translate_key(-1) is None


def test_translate_key_arrows():
    assert translate_key(curses.KEY_UP) == KEY_UP
    assert translate_key(curses.KEY_DOWN) == KEY_DOWN
    assert translate_key(curses.KEY_LEFT) == KEY_LEFT
    assert translate_key(curses.KEY_RIGHT) == KEY_RIGHT


def test_translate_key_named():
    assert translate_key(27) == KEY_ESCAPE
    assert translate_key(32) == KEY_SPACE
    assert translate_key(9) == KEY_TAB
    assert translate_key(10) == KEY_ENTER
    assert translate_key(13) == KEY_ENTER
    assert translate_key(127) == KEY_BACKSPACE


def test_translate_key_ascii():
    assert translate_key(ord("a")) == "a"
    assert translate_key(ord("Z")) == "Z"
    assert translate_key(ord("5")) == "5"


def test_translate_key_unknown():
    # Very large codes with no mapping
    assert translate_key(9999) is None


# --- KeyState ---

def test_keystate_just_pressed_on_first_frame():
    term = FakeTerminal()
    ks = KeyState()
    term.queue_keys(ord("a"))
    ks.update(term)
    assert ks.just_pressed("a")
    assert ks.is_down("a")


def test_keystate_just_pressed_only_once():
    term = FakeTerminal()
    ks = KeyState()
    term.queue_keys(ord("a"))
    ks.update(term)
    assert ks.just_pressed("a")
    # Second frame: same key still held (from OS repeat), but not just_pressed
    term.queue_keys(ord("a"))
    ks.update(term)
    assert not ks.just_pressed("a")
    assert ks.is_down("a")


def test_keystate_is_down_until_hold_expires():
    term = FakeTerminal()
    ks = KeyState(hold_time=0.05)
    term.queue_keys(ord("a"))
    ks.update(term)
    assert ks.is_down("a")
    # No new events; after hold_time, should be released
    time.sleep(0.07)
    ks.update(term)
    assert not ks.is_down("a")
    assert not ks.just_pressed("a")


def test_keystate_no_input_returns_empty():
    term = FakeTerminal()
    ks = KeyState()
    ks.update(term)
    assert not ks.is_down("a")
    assert not ks.just_pressed("a")


def test_keystate_conflicting_keys_cancel():
    term = FakeTerminal()
    ks = KeyState(hold_time=1.0)
    term.queue_keys(curses.KEY_UP)
    ks.update(term)
    assert ks.is_down(KEY_UP)
    # Press DOWN — should cancel UP
    term.queue_keys(curses.KEY_DOWN)
    ks.update(term)
    assert ks.is_down(KEY_DOWN)
    assert not ks.is_down(KEY_UP)


def test_keystate_conflicting_left_right():
    term = FakeTerminal()
    ks = KeyState(hold_time=1.0)
    term.queue_keys(curses.KEY_LEFT)
    ks.update(term)
    term.queue_keys(curses.KEY_RIGHT)
    ks.update(term)
    assert ks.is_down(KEY_RIGHT)
    assert not ks.is_down(KEY_LEFT)


def test_keystate_non_conflicting_keys_coexist():
    term = FakeTerminal()
    ks = KeyState(hold_time=1.0)
    term.queue_keys(curses.KEY_UP, curses.KEY_LEFT)
    ks.update(term)
    assert ks.is_down(KEY_UP)
    assert ks.is_down(KEY_LEFT)


def test_keystate_debounce_limits_firing_rate():
    term = FakeTerminal()
    ks = KeyState(hold_time=1.0, debounce=0.05)
    term.queue_keys(ord("a"))
    ks.update(term)
    assert ks.is_down("a")  # first fire
    # Immediate second update: debounce should suppress firing
    term.queue_keys(ord("a"))
    ks.update(term)
    assert not ks.is_down("a")
    # After debounce elapses, fires again
    time.sleep(0.06)
    term.queue_keys(ord("a"))
    ks.update(term)
    assert ks.is_down("a")


def test_keystate_no_debounce_fires_every_frame():
    term = FakeTerminal()
    ks = KeyState(hold_time=1.0, debounce=0)
    term.queue_keys(ord("a"))
    ks.update(term)
    assert ks.is_down("a")
    ks.update(term)  # no new events, but still held
    assert ks.is_down("a")
    ks.update(term)
    assert ks.is_down("a")


def test_keystate_just_pressed_clears_each_frame():
    term = FakeTerminal()
    ks = KeyState()
    term.queue_keys(ord("a"))
    ks.update(term)
    assert ks.just_pressed("a")
    ks.update(term)
    assert not ks.just_pressed("a")


def test_keystate_drains_multiple_keys_in_one_frame():
    term = FakeTerminal()
    ks = KeyState()
    term.queue_keys(ord("a"), ord("b"), ord("c"))
    ks.update(term)
    assert ks.just_pressed("a")
    assert ks.just_pressed("b")
    assert ks.just_pressed("c")
