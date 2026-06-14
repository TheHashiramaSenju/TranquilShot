import rclpy
from rclpy.node import Node
from tranq_interfaces.msg import FusedTarget, TrackedTarget
from tranq_tracker.kalman_filter import KalmanTracker
from tranq_tracker.target_arbitration import TargetArbitration

class TrackerNode(Node):
    def __init__(self):
        super().__init__('tracker_node')
        self.declare_parameter('process_noise', 0.01)
        self.declare_parameter('measurement_noise', 0.1)
        self.declare_parameter('max_lost_frames', 15)
        self.declare_parameter('min_distance_switch_m', 2.0)

        pn   = self.get_parameter('process_noise').value
        mn   = self.get_parameter('measurement_noise').value
        mlf  = self.get_parameter('max_lost_frames').value
        mds  = self.get_parameter('min_distance_switch_m').value

        self._kf   = KalmanTracker(pn, mn)
        self._arb  = TargetArbitration(mds)
        self._lost = 0
        self._max_lost = mlf
        self._track_id = 0

        self.create_subscription(FusedTarget, '/fused_targets', self._on_fused, 10)
        self._pub = self.create_publisher(TrackedTarget, '/tracked_target', 10)
        self.get_logger().info('tracker_node ready')

    def _on_fused(self, msg: FusedTarget):
        selected = self._arb.select([msg])
        if selected is None:
            self._lost += 1
            if self._lost > self._max_lost:
                self._kf.initialized = False
                self._lost = 0
            return

        cx = selected.detection.bbox_x + selected.detection.bbox_w / 2.0
        cy = selected.detection.bbox_y + selected.detection.bbox_h / 2.0
        d  = selected.depth_1

        if not self._kf.initialized:
            self._kf.init(cx, cy, d)
            self._track_id += 1

        self._kf.predict()
        state = self._kf.update(cx, cy, d)
        self._lost = 0

        tt = TrackedTarget()
        tt.fused      = selected
        tt.track_id   = self._track_id
        tt.centroid_x = float(state[0])
        tt.centroid_y = float(state[1])
        tt.distance   = float(state[2])
        tt.lost_frames = self._lost
        self._pub.publish(tt)

def main():
    rclpy.init()
    node = TrackerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
