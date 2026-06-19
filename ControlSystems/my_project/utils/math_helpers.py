import time
from config import CFG


class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, output_limit: float):
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._output_limit = output_limit
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = time.monotonic()

    def update(self, error: float) -> float:
        now = time.monotonic()
        dt = now - self._prev_time
        if dt <= 0.0:
            return 0.0

        self._integral += error * dt
        self._integral = max(
            -CFG.pid.INTEGRAL_WINDUP_LIMIT,
            min(CFG.pid.INTEGRAL_WINDUP_LIMIT, self._integral)
        )

        derivative = (error - self._prev_error) / dt
        output = (self._kp * error) + (self._ki * self._integral) + (self._kd * derivative)
        output = max(-self._output_limit, min(self._output_limit, output))

        self._prev_error = error
        self._prev_time = now
        return output

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0
        self._prev_time = time.monotonic()


def pixel_error_to_angle_rad(pixel_error: float, frame_width: int, hfov_deg: float) -> float:
    import math
    return math.radians((pixel_error / frame_width) * hfov_deg)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
