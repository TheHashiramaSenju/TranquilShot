import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from tranq_interfaces.msg import Detection
from tranq_detector.model_loader import ModelLoader
import numpy as np

class DetectorNode(Node):
    def __init__(self):
        super().__init__('detector_node')
        self.declare_parameter('model_path', 'models/best.pt')
        self.declare_parameter('backend', 'ultralytics')
        self.declare_parameter('confidence_threshold', 0.70)
        self.declare_parameter('input_width', 640)
        self.declare_parameter('input_height', 640)
        self.declare_parameter('target_class_id', 0)
        self.declare_parameter('use_coral_tpu', False)

        model_path    = self.get_parameter('model_path').value
        backend       = self.get_parameter('backend').value
        conf_thresh   = self.get_parameter('confidence_threshold').value
        target_cls    = self.get_parameter('target_class_id').value

        self._bridge = CvBridge()
        self._loader = ModelLoader(model_path, backend, target_cls, conf_thresh)

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.create_subscription(Image, '/camera/image_raw', self._on_frame, sensor_qos)
        self._pub = self.create_publisher(Detection, '/detections', 10)
        self.get_logger().info('detector_node ready')

    def _on_frame(self, msg: Image):
        frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
        raw_detections = self._loader.infer(frame)
        for rd in raw_detections:
            det = Detection()
            det.header = msg.header
            det.conf     = rd.conf
            det.class_id = rd.class_id
            det.bbox_x   = rd.bbox_x
            det.bbox_y   = rd.bbox_y
            det.bbox_w   = rd.bbox_w
            det.bbox_h   = rd.bbox_h
            self._pub.publish(det)

def main():
    rclpy.init()
    node = DetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
