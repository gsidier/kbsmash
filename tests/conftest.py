class FakeTerminal:
    """In-memory stand-in for Terminal. Captures queued chars and frame
    boundaries, and serves queued raw key codes from get_key_raw()."""

    def __init__(self):
        self.writes = []  # list of (x, y, char, fg, bg)
        self.refreshed = 0
        self.frames_begun = 0
        self.frames_ended = 0
        self._key_queue = []
        self.started = True

    def begin_frame(self):
        self.frames_begun += 1

    def queue_char(self, x, y, char, fg, bg):
        self.writes.append((x, y, char, fg, bg))

    def end_frame(self):
        self.frames_ended += 1
        self.refreshed += 1

    def write_char(self, x, y, char, fg, bg):
        self.begin_frame()
        self.queue_char(x, y, char, fg, bg)
        self.end_frame()

    def refresh(self):
        self.refreshed += 1

    def queue_keys(self, *raws):
        self._key_queue.extend(raws)

    def get_key_raw(self):
        if self._key_queue:
            return self._key_queue.pop(0)
        return -1
