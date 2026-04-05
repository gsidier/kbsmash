class FakeTerminal:
    """In-memory stand-in for Terminal. Captures write_char() calls and
    serves queued raw key codes from get_key_raw()."""

    def __init__(self):
        self.writes = []  # list of (x, y, char, fg, bg)
        self.refreshed = 0
        self._key_queue = []
        self.started = True

    def write_char(self, x, y, char, fg, bg):
        self.writes.append((x, y, char, fg, bg))

    def refresh(self):
        self.refreshed += 1

    def queue_keys(self, *raws):
        self._key_queue.extend(raws)

    def get_key_raw(self):
        if self._key_queue:
            return self._key_queue.pop(0)
        return -1
