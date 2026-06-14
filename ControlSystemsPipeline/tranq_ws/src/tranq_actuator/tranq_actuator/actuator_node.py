import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from tranq_interfaces.msg import ControlError
from tranq_interfaces.srv import ArmActuator, SetFireRange
from tranq_actuator.fire_condition import FireCondition

class ActuatorNode(Node):
    def __init__(self):
        super().__init__('actuator_node')
        self.declare_parameter('fire_range_m', 15.0)
        self.declare_parameter('crosshair_tolerance_px', 5.0)
        self.declare_parameter('default_armed', False)

        fire_range = self.get_parameter('fire_range_m').value
        tolerance  = self.get_parameter('crosshair_tolerance_px').value
        self._armed = self.get_parameter('default_armed').value
        self._fire_range = fire_range

        self._condition = FireCondition(fire_range, tolerance)

        self.create_subscription(ControlError, '/control_error', self._on_error, 10)
        self._pub = self.create_publisher(Bool, '/fire_trigger', 10)
        self.create_service(ArmActuator, '/arm_actuator', self._arm_cb)
        self.create_service(SetFireRange, '/set_fire_range', self._range_cb)
        self.get_logger().info(f'actuator_node ready — armed={self._armed}')

    def _on_error(self, msg: ControlError):
        if self._condition.evaluate(msg, self._armed):
            self._pub.publish(Bool(data=True))
            self._armed = False
            self.get_logger().warn(
                f'FIRE TRIGGERED — range={msg.range:.2f}m ex={msg.error_x:.1f}px ey={msg.error_y:.1f}px')
        else:
            self._pub.publish(Bool(data=False))

    def _arm_cb(self, request: ArmActuator.Request,
                response: ArmActuator.Response) -> ArmActuator.Response:
        self._armed = request.arm
        response.success = True
        response.armed   = self._armed
        self.get_logger().info(f'Actuator armed={self._armed}')
        return response

    def _range_cb(self, request: SetFireRange.Request,
                  response: SetFireRange.Response) -> SetFireRange.Response:
        self._fire_range = request.fire_range_m
        self._condition  = FireCondition(
            self._fire_range,
            self.get_parameter('crosshair_tolerance_px').value)
        response.success = True
        response.applied_fire_range_m = self._fire_range
        self.get_logger().info(f'Fire range updated to {self._fire_range}m')
        return response

def main():
    rclpy.init()
    node = ActuatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
