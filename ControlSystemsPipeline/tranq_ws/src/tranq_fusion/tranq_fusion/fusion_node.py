import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Range
from std_msgs.msg import Float32
from tranq_interfaces.msg import Detection, FusedTarget
from tranq_fusion.gates import GateRunner

class FusionNode(Node):
    def __init__(self):
        super().__init__('fusion_node')
        for name, default in [
            ('depth_min_m', 0.5), ('depth_max_m', 30.0),
            ('depth_variance_threshold', 0.05), ('size_tolerance', 0.45),
            ('elephant_height_m', 2.5), ('optical_flow_threshold', 0.0),
            ('confidence_threshold', 0.70), ('temporal_persist_frames', 1),
            ('camera_focal_length_px', 480.0),
        ]:
            self.declare_parameter(name, default)

        params = {n: self.get_parameter(n).value for n in [
            'depth_min_m', 'depth_max_m', 'depth_variance_threshold', 'size_tolerance',
            'elephant_height_m', 'optical_flow_threshold', 'confidence_threshold',
            'temporal_persist_frames', 'camera_focal_length_px',
        ]}
        self._runner = GateRunner(params)
        self._depth_1 = 8.0
        self._depth_2 = 8.2
        self._flow    = 1.0

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=1)

        self.create_subscription(Detection, '/detections', self._on_detection, 10)
        self.create_subscription(Range, '/range_1', self._on_range1, sensor_qos)
        self.create_subscription(Range, '/range_2', self._on_range2, sensor_qos)
        self.create_subscription(Float32, '/optical_flow/magnitude', self._on_flow, sensor_qos)
        self._pub = self.create_publisher(FusedTarget, '/fused_targets', 10)
        self.get_logger().info('fusion_node ready')

    def _on_range1(self, msg: Range):
        self._depth_1 = msg.range if msg.range > 0.05 else self._depth_1

    def _on_range2(self, msg: Range):
        self._depth_2 = msg.range if msg.range > 0.05 else self._depth_2

    def _on_flow(self, msg: Float32):
        self._flow = msg.data

    def _on_detection(self, msg: Detection):
        ft = self._runner.run(msg, self._depth_1, self._depth_2, self._flow)
        self._pub.publish(ft)

def main():
    rclpy.init()
    node = FusionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
