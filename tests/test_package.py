"""Smoke test that the public API surface is importable."""


def test_import_public_api():
    import kbsmash

    # Function-based API
    assert callable(kbsmash.start)
    assert callable(kbsmash.stop)
    assert callable(kbsmash.clear)
    assert callable(kbsmash.put)
    assert callable(kbsmash.text)
    assert callable(kbsmash.rect)
    assert callable(kbsmash.fill)
    assert callable(kbsmash.hline)
    assert callable(kbsmash.vline)
    assert callable(kbsmash.draw)
    assert callable(kbsmash.get_key)
    assert callable(kbsmash.update_keys)
    assert callable(kbsmash.key_down)
    assert callable(kbsmash.key_pressed)
    assert callable(kbsmash.screen_width)
    assert callable(kbsmash.screen_height)
    assert callable(kbsmash.dt)

    # Class-based API
    assert kbsmash.Game is not None

    # Key constants
    assert kbsmash.KEY_UP == "KEY_UP"
    assert kbsmash.KEY_DOWN == "KEY_DOWN"
    assert kbsmash.KEY_ESCAPE == "KEY_ESCAPE"

    # Colors
    assert kbsmash.BLACK == 0
    assert kbsmash.WHITE == 7
    assert kbsmash.BRIGHT_WHITE == 15

    # Modes
    assert kbsmash.ASCII == "ascii"
    assert kbsmash.EMOJI == "emoji"

    # Style helper
    assert callable(kbsmash.color)
