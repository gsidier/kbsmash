import time

from kbsmash._timing import Timer


def test_timer_initial_dt_zero():
    t = Timer(fps=30)
    assert t.dt == 0.0


def test_timer_wait_updates_dt():
    t = Timer(fps=60)
    time.sleep(0.01)
    t.wait()
    assert t.dt >= 0.01


def test_timer_enforces_frame_time():
    t = Timer(fps=50)  # 20ms per frame
    start = time.monotonic()
    t.wait()
    elapsed = time.monotonic() - start
    # Should have slept to reach ~20ms
    assert elapsed >= 0.015  # generous lower bound


def test_timer_no_fps_no_sleep():
    t = Timer(fps=0)
    start = time.monotonic()
    t.wait()
    elapsed = time.monotonic() - start
    assert elapsed < 0.01  # should return almost immediately


def test_timer_does_not_oversleep_when_frame_already_late():
    t = Timer(fps=1000)  # 1ms per frame
    time.sleep(0.02)  # blow past the frame budget
    start = time.monotonic()
    t.wait()
    elapsed = time.monotonic() - start
    # Should not sleep — already over budget
    assert elapsed < 0.005
