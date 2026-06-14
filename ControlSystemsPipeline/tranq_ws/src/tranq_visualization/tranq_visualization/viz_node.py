import cv2
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, Range
from std_msgs.msg import Bool
from tranq_interfaces.msg import Detection, FusedTarget, TrackedTarget, ControlError

class VizNode(Node):
    def __init__(self):
        super().__init__('viz_node')
        self.declare_parameter('window_name', 'TranquilShot Vision HUD')
        self.declare_parameter('show_window', True)
        self.declare_parameter('publish_annotated', True)
        self.declare_parameter('image_topic', '/camera/image_raw')

        self.window_name = self.get_parameter('window_name').value
        self.show_window = self.get_parameter('show_window').value
        self.publish_annotated = self.get_parameter('publish_annotated').value
        image_topic = self.get_parameter('image_topic').value

        self.bridge = CvBridge()
        self.last_detection = None
        self.last_fused = None
        self.last_tracked = None
        self.last_error = None
        self.last_fire = False
        self.range_1 = 0.0
        self.range_2 = 0.0

        self.create_subscription(Image, image_topic, self.on_image, 10)
        self.create_subscription(Detection, '/detections', self.on_detection, 10)
        self.create_subscription(FusedTarget, '/fused_targets', self.on_fused, 10)
        self.create_subscription(TrackedTarget, '/tracked_target', self.on_tracked, 10)
        self.create_subscription(ControlError, '/control_error', self.on_error, 10)
        self.create_subscription(Bool, '/fire_trigger', self.on_fire, 10)
        self.create_subscription(Range, '/range_1', self.on_range1, 10)
        self.create_subscription(Range, '/range_2', self.on_range2, 10)
        self.pub = self.create_publisher(Image, '/camera/annotated', 10)
        self.get_logger().info('viz_node ready')

    def on_detection(self, msg):
        self.last_detection = msg

    def on_fused(self, msg):
        self.last_fused = msg

    def on_tracked(self, msg):
        self.last_tracked = msg

    def on_error(self, msg):
        self.last_error = msg

    def on_fire(self, msg):
        self.last_fire = bool(msg.data)

    def on_range1(self, msg):
        self.range_1 = float(msg.range)

    def on_range2(self, msg):
        self.range_2 = float(msg.range)

    def draw_panel(self, img):
        overlay = img.copy()
        cv2.rectangle(overlay, (10, 10), (430, 220), (20, 20, 20), -1)
        img[:] = cv2.addWeighted(overlay, 0.42, img, 0.58, 0)
        y = 35
        lines = [
            'TRANQUILSHOT AUTONOMOUS TARGETING HUD',
            f'Range-1: {self.range_1:.2f} m',
            f'Range-2: {self.range_2:.2f} m',
        ]
        if self.last_fused is not None:
            lines += [
                f'Gate Confidence: {self.last_fused.gate_confidence}',
                f'Gate Depth:      {self.last_fused.gate_depth}',
                f'Gate Size:       {self.last_fused.gate_size}',
                f'Gate Motion:     {self.last_fused.gate_motion}',
                f'Depth Variance:  {self.last_fused.depth_variance:.3f}',
                f'VALID TARGET:    {self.last_fused.is_valid}',
            ]
        if self.last_error is not None:
            lines += [
                f'Error X: {self.last_error.error_x:.1f}px',
                f'Error Y: {self.last_error.error_y:.1f}px',
                f'Ready To Fire: {self.last_error.ready_to_fire}',
            ]
        status_color = (0, 0, 255) if self.last_fire else (0, 220, 255)
        lines += [f'FIRE STATE: {self.last_fire}']
        for i, text in enumerate(lines):
            color = (255, 255, 255)
            if 'VALID TARGET' in text:
                color = (0, 255, 0) if 'True' in text else (0, 180, 255)
            if 'FIRE STATE' in text:
                color = status_color
            cv2.putText(img, text, (22, y + i * 18), cv2.FONT_HERSHEY_SIMPLEX, 0.50, color, 1, cv2.LINE_AA)

    def draw_target(self, img):
        det = self.last_detection
        if det is None:
            cv2.putText(img, 'No detection yet', (30, img.shape[0] - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
            return
        x1 = int(det.bbox_x)
        y1 = int(det.bbox_y)
        x2 = int(det.bbox_x + det.bbox_w)
        y2 = int(det.bbox_y + det.bbox_h)
        valid = self.last_fused.is_valid if self.last_fused is not None else False
        color = (0, 255, 0) if valid else (0, 180, 255)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        label = f'elephant conf={det.conf:.2f}'
        cv2.putText(img, label, (x1, max(25, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA)
        if self.last_tracked is not None:
            cx = int(self.last_tracked.centroid_x)
            cy = int(self.last_tracked.centroid_y)
            cv2.drawMarker(img, (cx, cy), (255, 255, 255), cv2.MARKER_CROSS, 24, 2)
            cv2.circle(img, (cx, cy), 18, (50, 200, 255), 2)
            cv2.putText(img, f'ID {self.last_tracked.track_id} {self.last_tracked.distance:.2f}m', (x1, y2 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        h, w = img.shape[:2]
        cv2.drawMarker(img, (w // 2, h // 2), (0, 0, 255), cv2.MARKER_TILTED_CROSS, 34, 2)
        cv2.circle(img, (w // 2, h // 2), 26, (0, 0, 255), 2)

    def on_image(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.draw_panel(frame)
        self.draw_target(frame)
        if self.publish_annotated:
            self.pub.publish(self.bridge.cv2_to_imgmsg(frame, encoding='bgr8'))
        if self.show_window:
            cv2.imshow(self.window_name, frame)
            cv2.waitKey(1)

def main():
    rclpy.init()
    node = VizNode()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
