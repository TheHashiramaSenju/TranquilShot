from collections import deque
from tranq_interfaces.msg import Detection

class TemporalGate:
    def __init__(self, persist_frames: int, conf_threshold: float):
        self._persist = persist_frames
        self._conf_thresh = conf_threshold
        self._history: deque = deque(maxlen=persist_frames)

    def evaluate(self, detection: Detection) -> bool:
        passes_conf = detection.conf >= self._conf_thresh
        self._history.append(passes_conf)
        return len(self._history) == self._persist and all(self._history)

    def reset(self):
        self._history.clear()
