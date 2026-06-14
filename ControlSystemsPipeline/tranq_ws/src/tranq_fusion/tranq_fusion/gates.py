from tranq_fusion.temporal_gate import TemporalGate
from tranq_fusion.depth_gate    import DepthGate
from tranq_fusion.size_gate     import SizeGate
from tranq_fusion.motion_gate   import MotionGate
from tranq_interfaces.msg import Detection, FusedTarget

class GateRunner:
    def __init__(self, params: dict):
        self._temporal = TemporalGate(
            params['temporal_persist_frames'], params['confidence_threshold'])
        self._depth = DepthGate(
            params['depth_min_m'], params['depth_max_m'], params['depth_variance_threshold'])
        self._size = SizeGate(
            params['elephant_height_m'], params['camera_focal_length_px'], params['size_tolerance'])
        self._motion = MotionGate(params['optical_flow_threshold'])

    def run(self, detection: Detection, depth_1: float, depth_2: float,
            flow_magnitude: float) -> FusedTarget:
        t = self._temporal.evaluate(detection)
        d, variance = self._depth.evaluate(depth_1, depth_2)
        s = self._size.evaluate(detection, depth_1)
        m = self._motion.evaluate(flow_magnitude)

        ft = FusedTarget()
        ft.detection       = detection
        ft.depth_1         = depth_1
        ft.depth_2         = depth_2
        ft.depth_variance  = variance
        ft.gate_confidence = t
        ft.gate_depth      = d
        ft.gate_size       = s
        ft.gate_motion     = m
        ft.is_valid        = t and d and s and m
        return ft
