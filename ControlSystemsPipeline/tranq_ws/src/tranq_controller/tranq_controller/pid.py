#!/usr/bin/env python3
"""
TranquilShot PID Controller â€” pid.py
Reusable PID class with:
  - Anti-windup integrator clamping
  - Derivative on error (simple, suitable for slow outer loop)
  - reset_integrator() for dead-band suppression
"""


class PID:
    def __init__(self, kp: float, ki: float, kd: float,
                 out_min: float, out_max: float,
                 integrator_max: float = 1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.out_min       = out_min
        self.out_max       = out_max
        self.int_max       = integrator_max

        self._integral     = 0.0
        self._prev_error   = 0.0

    def compute(self, error: float, dt: float) -> float:
        """Compute PID output. dt in seconds."""
        # Proportional term
        p = self.kp * error

        # Integral term with anti-windup clamping
        self._integral += error * dt
        self._integral  = max(-self.int_max, min(self.int_max, self._integral))
        i = self.ki * self._integral

        # Derivative term
        d = self.kd * (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        output = p + i + d
        return max(self.out_min, min(self.out_max, output))

    def reset_integrator(self) -> None:
        """Zero the integrator â€” call when inside dead-band."""
        self._integral = 0.0
