class MotionGate:
    def __init__(self, flow_threshold: float):
        self._threshold = flow_threshold

    def evaluate(self, flow_magnitude: float) -> bool:
        return flow_magnitude >= self._threshold
