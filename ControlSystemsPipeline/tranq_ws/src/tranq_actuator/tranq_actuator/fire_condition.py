from tranq_interfaces.msg import ControlError

class FireCondition:
    def __init__(self, fire_range_m: float, crosshair_tolerance_px: float):
        self._fire_range  = fire_range_m
        self._tolerance   = crosshair_tolerance_px

    def evaluate(self, error: ControlError, is_armed: bool) -> bool:
        return (
            is_armed and
            error.ready_to_fire and
            error.range <= self._fire_range and
            abs(error.error_x) <= self._tolerance and
            abs(error.error_y) <= self._tolerance
        )
