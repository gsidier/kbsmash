import pytest

from kbsmash._screen import ScreenBuffer, Style, color, _is_wide, ASCII, EMOJI
from kbsmash._terminal import WHITE, BLACK, RED, GREEN, YELLOW, BLUE
from conftest import FakeTerminal


def make_screen(w=10, h=5, mode=ASCII):
    return ScreenBuffer(w, h, FakeTerminal(), mode=mode)


# --- _is_wide ---

def test_is_wide_ascii():
    assert not _is_wide("a")
    assert not _is_wide(" ")
    assert not _is_wide("@")


def test_is_wide_emoji():
    assert _is_wide("🍎")
    assert _is_wide("🟢")
    assert _is_wide("⬜")


def test_is_wide_multichar():
    # Compound emoji sequences
    assert _is_wide("👨‍👩‍👧")


# --- Style / color ---

def test_style_defaults_bg_to_black():
    s = Style(RED)
    assert s.fg == RED
    assert s.bg == BLACK


def test_style_explicit_bg():
    s = Style(RED, BLUE)
    assert s.fg == RED
    assert s.bg == BLUE


def test_color_helper():
    s = color(GREEN, YELLOW)
    assert isinstance(s, Style)
    assert s.fg == GREEN
    assert s.bg == YELLOW


def test_color_helper_default_bg():
    s = color(GREEN)
    assert s.bg == BLACK


# --- ScreenBuffer construction ---

def test_screen_dimensions():
    s = make_screen(20, 10)
    assert s.width == 20
    assert s.height == 10
    assert s.mode == ASCII


def test_screen_invalid_mode():
    with pytest.raises(ValueError):
        ScreenBuffer(10, 5, FakeTerminal(), mode="3d")


def test_screen_emoji_mode():
    s = make_screen(mode=EMOJI)
    assert s.mode == EMOJI


# --- put() ---

def test_put_in_bounds():
    s = make_screen()
    s.put(2, 1, "X")
    assert s._buf[1][2] == ("X", WHITE, BLACK)


def test_put_with_colors():
    s = make_screen()
    s.put(0, 0, "A", fg=RED, bg=BLUE)
    assert s._buf[0][0] == ("A", RED, BLUE)


def test_put_with_style():
    s = make_screen()
    s.put(0, 0, "A", style=color(YELLOW, GREEN))
    assert s._buf[0][0] == ("A", YELLOW, GREEN)


def test_put_out_of_bounds_clipped():
    s = make_screen(5, 3)
    # These should all silently do nothing
    s.put(-1, 0, "X")
    s.put(0, -1, "X")
    s.put(5, 0, "X")
    s.put(0, 3, "X")
    s.put(100, 100, "X")
    # Buffer unchanged
    for row in s._buf:
        for cell in row:
            assert cell == (" ", WHITE, BLACK)


def test_put_ascii_rejects_emoji():
    s = make_screen(mode=ASCII)
    with pytest.raises(ValueError, match="not allowed in ASCII"):
        s.put(0, 0, "🍎")


def test_put_emoji_rejects_ascii():
    s = make_screen(mode=EMOJI)
    with pytest.raises(ValueError, match="not allowed in emoji"):
        s.put(0, 0, "@")


def test_put_space_allowed_in_both_modes():
    ascii_s = make_screen(mode=ASCII)
    emoji_s = make_screen(mode=EMOJI)
    ascii_s.put(0, 0, " ")  # no raise
    emoji_s.put(0, 0, " ")  # no raise


# --- text() ---

def test_text_ascii():
    s = make_screen()
    s.text(1, 2, "hi", fg=RED)
    assert s._buf[2][1] == ("h", RED, BLACK)
    assert s._buf[2][2] == ("i", RED, BLACK)


def test_text_clipped():
    s = make_screen(5, 3)
    s.text(3, 0, "hello")  # only "he" fits
    assert s._buf[0][3] == ("h", WHITE, BLACK)
    assert s._buf[0][4] == ("e", WHITE, BLACK)


def test_text_with_style():
    s = make_screen()
    s.text(0, 0, "ok", style=color(GREEN, BLUE))
    assert s._buf[0][0] == ("o", GREEN, BLUE)
    assert s._buf[0][1] == ("k", GREEN, BLUE)


def test_text_emoji_mode_packs_pairs():
    s = make_screen(mode=EMOJI)
    s.text(0, 0, "1234", fg=RED)
    assert s._buf[0][0] == ("12", RED, BLACK)
    assert s._buf[0][1] == ("34", RED, BLACK)


def test_text_emoji_mode_pads_odd_length():
    s = make_screen(mode=EMOJI)
    s.text(0, 0, "abc")
    assert s._buf[0][0] == ("ab", WHITE, BLACK)
    assert s._buf[0][1] == ("c ", WHITE, BLACK)


def test_text_emoji_mode_rejects_wide_chars():
    s = make_screen(mode=EMOJI)
    with pytest.raises(ValueError, match="wide char"):
        s.text(0, 0, "x🍎")


def test_text_emoji_mode_clipped():
    s = make_screen(5, 3, mode=EMOJI)
    s.text(4, 0, "123456")  # only "12" fits at cell 4
    assert s._buf[0][4] == ("12", WHITE, BLACK)


# --- clear() / fill() ---

def test_clear_default_space():
    s = make_screen()
    s.put(1, 1, "X")
    s.clear()
    assert s._buf[1][1] == (" ", WHITE, BLACK)


def test_clear_custom_char():
    s = make_screen()
    s.clear(".")
    for row in s._buf:
        for cell in row:
            assert cell[0] == "."


def test_fill():
    s = make_screen(10, 5)
    s.fill(2, 1, 3, 2, char="#", fg=RED)
    for y in range(1, 3):
        for x in range(2, 5):
            assert s._buf[y][x] == ("#", RED, BLACK)
    # outside untouched
    assert s._buf[0][0] == (" ", WHITE, BLACK)
    assert s._buf[1][5] == (" ", WHITE, BLACK)


# --- rect() ---

def test_rect_default_box_chars_ascii():
    s = make_screen(10, 5)
    s.rect(0, 0, 5, 3)
    assert s._buf[0][0] == ("┌", WHITE, BLACK)
    assert s._buf[0][4] == ("┐", WHITE, BLACK)
    assert s._buf[2][0] == ("└", WHITE, BLACK)
    assert s._buf[2][4] == ("┘", WHITE, BLACK)
    assert s._buf[0][1] == ("─", WHITE, BLACK)
    assert s._buf[1][0] == ("│", WHITE, BLACK)


def test_rect_custom_char():
    s = make_screen(10, 5)
    s.rect(0, 0, 4, 3, char="#")
    assert s._buf[0][0] == ("#", WHITE, BLACK)
    assert s._buf[0][3] == ("#", WHITE, BLACK)
    assert s._buf[2][0] == ("#", WHITE, BLACK)
    assert s._buf[2][3] == ("#", WHITE, BLACK)
    # Interior untouched
    assert s._buf[1][1] == (" ", WHITE, BLACK)


def test_rect_too_small():
    s = make_screen()
    s.rect(0, 0, 1, 3)  # width < 2
    s.rect(0, 0, 3, 1)  # height < 2
    # Nothing drawn
    for row in s._buf:
        for cell in row:
            assert cell == (" ", WHITE, BLACK)


def test_rect_emoji_mode_requires_char():
    s = make_screen(mode=EMOJI)
    with pytest.raises(ValueError, match="requires a char"):
        s.rect(0, 0, 5, 3)


def test_rect_emoji_mode_with_char():
    s = make_screen(mode=EMOJI)
    s.rect(0, 0, 3, 3, char="⬜")
    assert s._buf[0][0] == ("⬜", WHITE, BLACK)


# --- hline / vline ---

def test_hline_default_ascii():
    s = make_screen()
    s.hline(1, 2, 3)
    for x in range(1, 4):
        assert s._buf[2][x] == ("─", WHITE, BLACK)


def test_hline_custom_char():
    s = make_screen()
    s.hline(0, 0, 5, char="=", fg=RED)
    for x in range(5):
        assert s._buf[0][x] == ("=", RED, BLACK)


def test_hline_emoji_requires_char():
    s = make_screen(mode=EMOJI)
    with pytest.raises(ValueError, match="requires a char"):
        s.hline(0, 0, 3)


def test_vline_default_ascii():
    s = make_screen()
    s.vline(1, 0, 3)
    for y in range(3):
        assert s._buf[y][1] == ("│", WHITE, BLACK)


def test_vline_custom_char():
    s = make_screen()
    s.vline(0, 0, 3, char="|", fg=RED)
    for y in range(3):
        assert s._buf[y][0] == ("|", RED, BLACK)


def test_vline_emoji_requires_char():
    s = make_screen(mode=EMOJI)
    with pytest.raises(ValueError, match="requires a char"):
        s.vline(0, 0, 3)


# --- draw() ---

def test_draw_writes_only_diffed_cells():
    term = FakeTerminal()
    s = ScreenBuffer(3, 2, term, mode=ASCII)
    s.put(1, 0, "X", fg=RED)
    s.draw()
    # Only the changed cell is written (prev snapshot matches initial clear)
    assert term.writes == [(1, 0, "X", RED, BLACK)]
    assert term.refreshed == 1


def test_draw_diffs_subsequent_frames():
    term = FakeTerminal()
    s = ScreenBuffer(3, 2, term, mode=ASCII)
    s.draw()
    term.writes.clear()
    # Second frame, nothing changed
    s.draw()
    assert term.writes == []


def test_draw_only_writes_changed_cells():
    term = FakeTerminal()
    s = ScreenBuffer(3, 2, term, mode=ASCII)
    s.draw()
    term.writes.clear()
    s.put(1, 0, "Z")
    s.draw()
    assert len(term.writes) == 1
    x, y, ch, fg, bg = term.writes[0]
    assert (x, y, ch) == (1, 0, "Z")


def test_draw_emoji_mode_doubles_x():
    term = FakeTerminal()
    s = ScreenBuffer(3, 2, term, mode=EMOJI)
    s.put(1, 0, "🍎")
    s.draw()
    # Find the apple write
    apples = [w for w in term.writes if w[2] == "🍎"]
    assert len(apples) == 1
    x, y, ch, fg, bg = apples[0]
    assert x == 2  # cell 1 * 2
    assert y == 0


def test_draw_emoji_mode_clears_with_two_spaces():
    term = FakeTerminal()
    s = ScreenBuffer(2, 1, term, mode=EMOJI)
    s.draw()
    # Should write two spaces for each cleared cell
    for (x, y, ch, fg, bg) in term.writes:
        assert ch == "  "
