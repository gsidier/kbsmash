from kbsmash._terminal import (
    _fg_code, _bg_code,
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
    BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW,
    BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE,
)


def test_fg_code_normal():
    assert _fg_code(BLACK) == 30
    assert _fg_code(RED) == 31
    assert _fg_code(GREEN) == 32
    assert _fg_code(YELLOW) == 33
    assert _fg_code(BLUE) == 34
    assert _fg_code(MAGENTA) == 35
    assert _fg_code(CYAN) == 36
    assert _fg_code(WHITE) == 37


def test_fg_code_bright():
    assert _fg_code(BRIGHT_BLACK) == 90
    assert _fg_code(BRIGHT_RED) == 91
    assert _fg_code(BRIGHT_GREEN) == 92
    assert _fg_code(BRIGHT_YELLOW) == 93
    assert _fg_code(BRIGHT_BLUE) == 94
    assert _fg_code(BRIGHT_MAGENTA) == 95
    assert _fg_code(BRIGHT_CYAN) == 96
    assert _fg_code(BRIGHT_WHITE) == 97


def test_bg_code_normal():
    assert _bg_code(BLACK) == 40
    assert _bg_code(RED) == 41
    assert _bg_code(WHITE) == 47


def test_bg_code_bright():
    assert _bg_code(BRIGHT_BLACK) == 100
    assert _bg_code(BRIGHT_RED) == 101
    assert _bg_code(BRIGHT_WHITE) == 107
