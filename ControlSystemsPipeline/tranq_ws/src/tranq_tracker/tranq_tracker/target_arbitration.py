from typing import List, Optional
from tranq_interfaces.msg import FusedTarget

class TargetArbitration:
    def __init__(self, min_distance_switch_m: float):
        self._switch_margin = min_distance_switch_m
        self._locked_id: Optional[int] = None

    def select(self, targets: List[FusedTarget]) -> Optional[FusedTarget]:
        valid = [t for t in targets if t.is_valid]
        if not valid:
            self._locked_id = None
            return None
        valid.sort(key=lambda t: t.depth_1)
        nearest = valid[0]
        if self._locked_id is None:
            self._locked_id = id(nearest)
            return nearest
        current = next((t for t in valid if id(t) == self._locked_id), None)
        if current is None:
            self._locked_id = id(nearest)
            return nearest
        if current.depth_1 - nearest.depth_1 > self._switch_margin:
            self._locked_id = id(nearest)
            return nearest
        return current
