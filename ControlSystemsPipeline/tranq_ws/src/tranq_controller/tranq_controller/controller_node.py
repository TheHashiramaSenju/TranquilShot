import rclpy
from rclpy.node import Node
from rclpy.time import Time
from geometry_msgs.msg import Twist
from tranq_interfaces.msg import TrackedTarget, ControlError
from tranq_controller.pid import PID

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        for name, default in [
            ('kp_yaw', 0.005), ('ki_yaw', 0.0001), ('kd_yaw', 0.001),
            ('kp_pitch', 0.005), ('ki_pitch', 0.0001), ('kd_pitch', 0.001),
            ('dead_band_px', 5.0), ('frame_width', 640), ('frame_height', 480),
            ('output_clamp', 0.5),
        ]:
            self.declare_parameter(name, default)

        clamp = self.get_parameter('output_clamp').value
        self._pid_yaw = PID(
            self.get_parameter('kp_yaw').value, self.get_parameter('ki_yaw').value,
            self.get_parameter('kd_yaw').value, -clamp, clamp, 1.0)
        self._pid_pitch = PID(
            self.get_parameter('kp_pitch').value, self.get_parameter('ki_pitch').value,
            self.get_parameter('kd_pitch').value, -clamp, clamp, 1.0)

        self._dead_band  = self.get_parameter('dead_band_px').value
        self._cx_center  = self.get_parameter('frame_width').value  / 2.0
        self._cy_center  = self.get_parameter('frame_height').value / 2.0
        self._last_stamp: Time = self.get_clock().now()

        self.create_subscription(TrackedTarget, '/tracked_target', self._on_target, 10)
        self._pub_cmd   = self.create_publisher(Twist, '/drone/cmd_vel', 10)
        self._pub_error = self.create_publisher(ControlError, '/control_error', 10)
        self.get_logger().info('controller_node ready')

    def _on_target(self, msg: TrackedTarget):
        now = self.get_clock().now()
        dt  = (now - self._last_stamp).nanoseconds / 1e9
        self._last_stamp = now

        ex = msg.centroid_x - self._cx_center
        ey = msg.centroid_y - self._cy_center

        cmd = Twist()
        if abs(ex) > self._dead_band or abs(ey) > self._dead_band:
            cmd.angular.z = -self._pid_yaw.compute(ex, dt)
            cmd.angular.y =  self._pid_pitch.compute(ey, dt)
        else:
            self._pid_yaw.reset()
            self._pid_pitch.reset()
        self._pub_cmd.publish(cmd)

        ce = ControlError()
        ce.error_x      = ex
        ce.error_y      = ey
        ce.range        = msg.distance
        ce.ready_to_fire = (
            msg.fused.is_valid and
            abs(ex) <= self._dead_band and
            abs(ey) <= self._dead_band
        )
        self._pub_error.publish(ce)

def main():
    rclpy.init()
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
