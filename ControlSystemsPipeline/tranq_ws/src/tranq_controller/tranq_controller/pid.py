class PID:
    def __init__(self, kp: float, ki: float, kd: float,
                 output_min: float, output_max: float, anti_windup_limit: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.anti_windup_limit = anti_windup_limit
        self._integral = 0.0
        self._prev_error = 0.0

    def compute(self, error: float, dt: float) -> float:
        if dt <= 0.0:
            return 0.0
        self._integral += error * dt
        self._integral = max(-self.anti_windup_limit,
                             min(self.anti_windup_limit, self._integral))
        derivative = (error - self._prev_error) / dt
        self._prev_error = error
        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        return max(self.output_min, min(self.output_max, output))

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
