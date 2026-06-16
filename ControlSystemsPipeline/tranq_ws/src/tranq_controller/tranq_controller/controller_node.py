#!/usr/bin/env python3
"""
TranquilShot â€” Dual-Axis PID Flight Controller Node
FIX: Completed truncated implementation. Added:
  - Full subscription + publisher setup
  - Dead-band suppression (reduces micro-corrections / motor wear)
  - Anti-windup via PID.reset_integrator()
  - dt guard (prevents division by zero on first callback)
  - ControlError telemetry publishing for tuning / logging
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from tranq_interfaces.msg import TrackedTarget, ControlError
from tranq_controller.pid import PID


class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')

        # â”€â”€ Declare ROS 2 parameters â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        params = {
            'kp_yaw':         0.005,
            'ki_yaw':         0.0001,
            'kd_yaw':         0.001,
            'kp_pitch':       0.005,
            'ki_pitch':       0.0001,
            'kd_pitch':       0.001,
            'dead_band_px':   5.0,
            'frame_width':    640,
            'frame_height':   480,
            'output_clamp':   0.4,
            'max_linear_speed': 2.0,
        }
        for name, default in params.items():
            self.declare_parameter(name, default)

        clamp = self.get_parameter('output_clamp').value

        self._pid_yaw = PID(
            self.get_parameter('kp_yaw').value,
            self.get_parameter('ki_yaw').value,
            self.get_parameter('kd_yaw').value,
            -clamp, clamp, integrator_max=1.0
        )
        self._pid_pitch = PID(
            self.get_parameter('kp_pitch').value,
            self.get_parameter('ki_pitch').value,
            self.get_parameter('kd_pitch').value,
            -clamp, clamp, integrator_max=1.0
        )

        self._db   = self.get_parameter('dead_band_px').value
        self._fw   = float(self.get_parameter('frame_width').value)
        self._fh   = float(self.get_parameter('frame_height').value)
        self._vmax = self.get_parameter('max_linear_speed').value

        # â”€â”€ Publishers / Subscribers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._sub      = self.create_subscription(
            TrackedTarget, '/tracked_target', self._cb, 10)
        self._pub_cmd  = self.create_publisher(Twist,        '/cmd_vel',       10)
        self._pub_err  = self.create_publisher(ControlError, '/control_error', 10)

        self._last_t = None
        self.get_logger().info('ControllerNode ready â€” awaiting /tracked_target')

    # â”€â”€ Main control callback â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _cb(self, msg: TrackedTarget):
        now = self.get_clock().now()
        dt  = (now - self._last_t).nanoseconds * 1e-9 if self._last_t else 0.033
        self._last_t = now
        dt = max(0.001, min(dt, 0.5))   # Guard against absurd dt values

        # Pixel error from frame centre
        ex = msg.cx - self._fw / 2.0
        ey = msg.cy - self._fh / 2.0

        # Dead-band: suppress jitter corrections (also resets integrator
        # to prevent windup when target is centred)
        if abs(ex) < self._db:
            ex = 0.0
            self._pid_yaw.reset_integrator()
        if abs(ey) < self._db:
            ey = 0.0
            self._pid_pitch.reset_integrator()

        # PID compute
        vz = self._pid_yaw.compute(ex,  dt)   # lateral / yaw rate
        vx = self._pid_pitch.compute(-ey, dt) # forward / pitch

        # Clamp to safe speed limits
        vz = max(-self._vmax, min(self._vmax, vz))
        vx = max(-self._vmax, min(self._vmax, vx))

        # Publish velocity command
        twist            = Twist()
        twist.linear.x   = vx
        twist.angular.z  = vz
        self._pub_cmd.publish(twist)

        # Publish telemetry for tuning / patent demo logging
        err              = ControlError()
        err.header.stamp = now.to_msg()
        err.error_x      = ex
        err.error_y      = ey
        err.output_vx    = vx
        err.output_vz    = vz
        self._pub_err.publish(err)


def main():
    rclpy.init()
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
