from typing import Tuple

class DepthGate:
    def __init__(self, depth_min: float, depth_max: float, variance_threshold: float):
        self._min = depth_min
        self._max = depth_max
        self._var_thresh = variance_threshold

    def evaluate(self, depth_1: float, depth_2: float) -> Tuple[bool, float]:
        variance = abs(depth_1 - depth_2)
        in_range = self._min <= depth_1 <= self._max and self._min <= depth_2 <= self._max
        has_variance = variance > self._var_thresh
        return in_range and has_variance, variance
