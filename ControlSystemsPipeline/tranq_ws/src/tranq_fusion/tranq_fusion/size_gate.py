from tranq_interfaces.msg import Detection

class SizeGate:
    def __init__(self, elephant_height_m: float, focal_length_px: float, tolerance: float):
        self._h = elephant_height_m
        self._f = focal_length_px
        self._tol = tolerance

    def evaluate(self, detection: Detection, depth: float) -> bool:
        if detection.bbox_h <= 0 or depth <= 0:
            return False
        expected = (self._h * self._f) / detection.bbox_h
        ratio = abs(expected - depth) / max(depth, 0.001)
        return ratio <= self._tol
