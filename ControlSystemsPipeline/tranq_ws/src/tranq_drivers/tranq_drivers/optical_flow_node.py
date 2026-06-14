import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from cv_bridge import CvBridge
import cv2
import numpy as np

class OpticalFlowNode(Node):
    def __init__(self):
        super().__init__('optical_flow_node')
        self.declare_parameter('max_corners', 50)
        self.declare_parameter('quality_level', 0.3)
        self.declare_parameter('min_distance', 7.0)
        self._bridge = CvBridge()
        self._prev_gray = None
        self._lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        self._feat_params = dict(
            maxCorners=self.get_parameter('max_corners').value,
            qualityLevel=self.get_parameter('quality_level').value,
            minDistance=self.get_parameter('min_distance').value,
            blockSize=7
        )
        self.create_subscription(Image, '/camera/image_raw', self._on_frame, 10)
        self._pub = self.create_publisher(Float32, '/optical_flow/magnitude', 10)
        self.get_logger().info('optical_flow_node ready')

    def _on_frame(self, msg: Image):
        frame = self._bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')
        if self._prev_gray is None:
            self._prev_gray = frame
            return
        p0 = cv2.goodFeaturesToTrack(self._prev_gray, mask=None, **self._feat_params)
        if p0 is None:
            self._pub.publish(Float32(data=0.0))
            self._prev_gray = frame
            return
        p1, st, _ = cv2.calcOpticalFlowPyrLK(self._prev_gray, frame, p0, None, **self._lk_params)
        good = p1[st == 1] - p0[st == 1]
        magnitude = float(np.mean(np.linalg.norm(good, axis=1))) if len(good) else 0.0
        self._pub.publish(Float32(data=magnitude))
        self._prev_gray = frame

def main():
    rclpy.init()
    node = OpticalFlowNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
