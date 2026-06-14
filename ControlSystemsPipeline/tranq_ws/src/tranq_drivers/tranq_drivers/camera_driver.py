import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np

class CameraDriver(Node):
    def __init__(self):
        super().__init__('camera_driver')
        self.declare_parameter('fps', 30)
        self.declare_parameter('width', 640)
        self.declare_parameter('height', 480)
        self._bridge = CvBridge()
        self._pub = self.create_publisher(Image, '/camera/image_raw', 10)
        fps = self.get_parameter('fps').value
        self.create_timer(1.0 / fps, self._capture)
        self.get_logger().info('camera_driver ready — awaiting picamera2 init')

    def _capture(self):
        # TODO Phase 3: replace with picamera2 capture
        # from picamera2 import Picamera2
        # frame = self._cam.capture_array()
        # msg = self._bridge.cv2_to_imgmsg(frame, encoding='rgb8')
        # self._pub.publish(msg)
        pass

def main():
    rclpy.init()
    node = CameraDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
