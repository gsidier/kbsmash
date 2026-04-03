import time


class Timer:
    def __init__(self, fps=30):
        self._fps = fps
        self._frame_time = 1.0 / fps if fps else 0
        self._last_draw = time.monotonic()
        self._dt = 0.0

    @property
    def dt(self):
        return self._dt

    def wait(self):
        now = time.monotonic()
        self._dt = now - self._last_draw
        if self._fps:
            elapsed = now - self._last_draw
            remaining = self._frame_time - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_draw = time.monotonic()
