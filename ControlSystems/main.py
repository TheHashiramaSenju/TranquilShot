from __future__ import annotations
import time
import sys
from enum import Enum, auto

from config import CFG
from hardware.camera_tpu import TPUDetector
from hardware.tof_sensors import DistanceSensor
from hardware.pixhawk_link import PixHawkController
from utils.math_helpers import PIDController, clamp
from utils.logger import FlightLogger, FlightRecord


class State(Enum):
    PREFLIGHT   = auto()
    TAKEOFF     = auto()
    SCANNING    = auto()
    APPROACHING = auto()
    TRACKING    = auto()
    LOITERING   = auto()
    FIRE        = auto()
    COOLDOWN    = auto()
    RTL         = auto()


class TranquilDrone:
    def __init__(self):
        self._camera   = TPUDetector()
        self._rangefinder = DistanceSensor()
        self._fc       = PixHawkController()
        self._logger   = FlightLogger()

        self._yaw_pid   = PIDController(
            CFG.pid.YAW_KP, CFG.pid.YAW_KI, CFG.pid.YAW_KD,
            CFG.kinematics.MAX_YAW_RATE_RDS
        )
        self._pitch_pid = PIDController(
            CFG.pid.PITCH_KP, CFG.pid.PITCH_KI, CFG.pid.PITCH_KD,
            CFG.kinematics.MAX_FORWARD_SPEED_MS
        )

        self._state            = State.PREFLIGHT
        self._occlusion_start  = 0.0
        self._cooldown_start   = 0.0
        self._center_x         = CFG.vision.FRAME_WIDTH  // 2
        self._center_y         = CFG.vision.FRAME_HEIGHT // 2

    def _transition(self, new_state: State) -> None:
        self._state = new_state
        if new_state in (State.SCANNING, State.TRACKING, State.APPROACHING):
            self._yaw_pid.reset()
            self._pitch_pid.reset()

    def _preflight(self) -> None:
        voltage = self._fc.get_battery_voltage()
        if voltage < CFG.safety.MIN_BATTERY_VOLTAGE:
            raise RuntimeError(f"Battery too low for flight: {voltage:.2f}V")
        self._fc.set_mode("GUIDED")
        self._transition(State.TAKEOFF)

    def _takeoff(self) -> None:
        self._fc.arm_and_takeoff(CFG.kinematics.TAKEOFF_ALTITUDE_M)
        self._transition(State.SCANNING)

    def _scanning(self) -> None:
        self._fc.send_velocity(0.0, 0.0, 0.0, CFG.kinematics.SCAN_YAW_RATE_RDS)

    def _compute_tracking_commands(self, cx: int, cy: int, dist_mm: int) -> tuple[float, float, float]:
        x_error = cx - self._center_x
        y_error = cy - self._center_y

        yaw_rate = self._yaw_pid.update(float(x_error))
        pitch_cmd = self._pitch_pid.update(float(y_error))

        if dist_mm < CFG.engagement.MIN_FIRING_DIST_MM:
            vx = -0.3
        elif dist_mm > CFG.engagement.MAX_FIRING_DIST_MM:
            vx = clamp(CFG.kinematics.MAX_FORWARD_SPEED_MS * 0.5, 0.0, CFG.kinematics.MAX_FORWARD_SPEED_MS)
        else:
            vx = clamp(
                (dist_mm - CFG.engagement.MIN_FIRING_DIST_MM) / 10000.0,
                0.0,
                CFG.kinematics.MAX_FORWARD_SPEED_MS * 0.4
            )

        return vx, yaw_rate, pitch_cmd

    def _is_aligned(self, cx: int, cy: int) -> bool:
        return (
            abs(cx - self._center_x) <= CFG.engagement.CENTER_TOLERANCE_PX and
            abs(cy - self._center_y) <= CFG.engagement.CENTER_TOLERANCE_PX
        )

    def _is_in_range(self, dist_mm: int) -> bool:
        return CFG.engagement.MIN_FIRING_DIST_MM <= dist_mm <= CFG.engagement.MAX_FIRING_DIST_MM

    def _run_heartbeat(self) -> None:
        detection  = self._camera.detect_target()
        dist_mm    = self._rangefinder.get_distance_mm()
        voltage    = self._fc.get_battery_voltage()
        fired_flag = False
        yaw_cmd    = 0.0
        pitch_cmd  = 0.0
        vx_cmd     = 0.0

        if voltage < CFG.safety.MIN_BATTERY_VOLTAGE:
            self._transition(State.RTL)

        if self._state == State.SCANNING:
            if detection is not None:
                self._occlusion_start = 0.0
                self._transition(State.APPROACHING)
            else:
                self._scanning()

        elif self._state == State.APPROACHING:
            if detection is None:
                if self._occlusion_start == 0.0:
                    self._occlusion_start = time.monotonic()
                if time.monotonic() - self._occlusion_start > CFG.timers.OCCLUSION_TIMEOUT_S:
                    self._fc.hover()
                    self._transition(State.SCANNING)
                elif self._fc.needs_velocity_refresh():
                    self._fc.send_velocity(vx_cmd, 0.0, 0.0, yaw_cmd)
            else:
                self._occlusion_start = 0.0
                vx_cmd, yaw_cmd, pitch_cmd = self._compute_tracking_commands(
                    detection.cx, detection.cy, dist_mm
                )
                self._fc.send_velocity(vx_cmd, 0.0, 0.0, yaw_cmd)
                if self._is_in_range(dist_mm):
                    self._transition(State.TRACKING)

        elif self._state == State.TRACKING:
            if detection is None:
                if self._occlusion_start == 0.0:
                    self._occlusion_start = time.monotonic()
                if time.monotonic() - self._occlusion_start > CFG.timers.OCCLUSION_TIMEOUT_S:
                    self._fc.hover()
                    self._transition(State.SCANNING)
                elif self._fc.needs_velocity_refresh():
                    self._fc.send_velocity(0.0, 0.0, 0.0, 0.0)
            else:
                self._occlusion_start = 0.0
                vx_cmd, yaw_cmd, pitch_cmd = self._compute_tracking_commands(
                    detection.cx, detection.cy, dist_mm
                )
                self._fc.send_velocity(vx_cmd, 0.0, 0.0, yaw_cmd)

                if not self._is_in_range(dist_mm):
                    self._transition(State.APPROACHING)
                elif self._is_aligned(detection.cx, detection.cy):
                    self._fc.hover()
                    self._transition(State.LOITERING)

        elif self._state == State.LOITERING:
            if detection is None:
                self._transition(State.SCANNING)
            else:
                vx_cmd, yaw_cmd, pitch_cmd = self._compute_tracking_commands(
                    detection.cx, detection.cy, dist_mm
                )
                self._fc.send_velocity(vx_cmd, 0.0, 0.0, yaw_cmd)
                if (
                    self._is_aligned(detection.cx, detection.cy)
                    and self._is_in_range(dist_mm)
                ):
                    self._transition(State.FIRE)

        elif self._state == State.FIRE:
            self._fc.fire_payload()
            fired_flag = True
            self._cooldown_start = time.monotonic()
            self._transition(State.COOLDOWN)

        elif self._state == State.COOLDOWN:
            self._fc.hover()
            if time.monotonic() - self._cooldown_start >= CFG.engagement.FIRING_COOLDOWN_S:
                self._transition(State.SCANNING)

        elif self._state == State.RTL:
            self._fc.return_to_launch()

        cx_log = detection.cx if detection else -1
        cy_log = detection.cy if detection else -1
        conf   = detection.confidence if detection else 0.0

        self._logger.write(FlightRecord(
            timestamp=time.time(),
            state=self._state.name,
            target_x=cx_log,
            target_y=cy_log,
            confidence=conf,
            distance_mm=dist_mm,
            yaw_cmd=yaw_cmd,
            pitch_cmd=pitch_cmd,
            vx_cmd=vx_cmd,
            battery_v=voltage,
            fired=fired_flag
        ))

    def run(self) -> None:
        try:
            self._preflight()
            self._takeoff()
            while self._state != State.RTL:
                loop_start = time.monotonic()
                self._run_heartbeat()
                elapsed = time.monotonic() - loop_start
                sleep_time = CFG.timers.HEARTBEAT_INTERVAL_S - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            self._fc.return_to_launch()
        finally:
            self._camera.close()
            self._rangefinder.close()
            self._fc.close()
            self._logger.close()


if __name__ == "__main__":
    drone = TranquilDrone()
    drone.run()
