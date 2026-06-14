import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
import threading

class VL53L1XDriver(Node):
    def __init__(self):
        super().__init__('vl53l1x_driver')
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('addr_sensor1', 0x29)
        self.declare_parameter('addr_sensor2', 0x30)
        self.declare_parameter('rate_hz', 30)
        self._pub1 = self.create_publisher(Range, '/range_1', 10)
        self._pub2 = self.create_publisher(Range, '/range_2', 10)
        rate = self.get_parameter('rate_hz').value
        self._lock = threading.Lock()
        self.create_timer(1.0 / rate, self._read)
        self.get_logger().info('vl53l1x_driver ready — awaiting smbus2 init')

    def _build_range_msg(self, distance_m: float, frame: str) -> Range:
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame
        msg.radiation_type = Range.INFRARED
        msg.field_of_view = 0.04
        msg.min_range = 0.05
        msg.max_range = 30.0
        msg.range = distance_m
        return msg

    def _read(self):
        # TODO Phase 3: replace with smbus2 reads
        # import smbus2, VL53L1X
        # d1 = sensor1.read_distance() / 1000.0
        # d2 = sensor2.read_distance() / 1000.0
        d1, d2 = 0.0, 0.0
        self._pub1.publish(self._build_range_msg(d1, 'tof_center_link'))
        self._pub2.publish(self._build_range_msg(d2, 'tof_offset_link'))

def main():
    rclpy.init()
    node = VL53L1XDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
