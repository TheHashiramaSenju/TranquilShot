from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

@dataclass(frozen=True)
class HardwareConfig:
    FC_CONNECTION_STRING: str = "tcp:127.0.0.1:5760"
    FC_BAUD_RATE: int = 921600
    FC_HEARTBEAT_TIMEOUT: int = 10
    TOF_I2C_BUS: int = 1
    TOF_I2C_ADDRESS: int = 0x29
    TOF_TIMING_BUDGET_MS: int = 50
    PAYLOAD_SERVO_CHANNEL: int = 9
    CAMERA_INDEX: int = 3

@dataclass(frozen=True)
class VisionConfig:
    TARGET_LABEL: str = "elephant"
    CONFIDENCE_THRESHOLD: float = 0.75
    FRAME_WIDTH: int = 640
    FRAME_HEIGHT: int = 480
    MODEL_PATH: Path = BASE_DIR / "models" / "target_edgetpu.tflite"
    LABELS_PATH: Path = BASE_DIR / "models" / "labels.txt"
    CAMERA_HFOV_DEG: float = 62.2

@dataclass(frozen=True)
class EngagementConfig:
    MIN_FIRING_DIST_MM: int = 5000
    MAX_FIRING_DIST_MM: int = 15000
    CENTER_TOLERANCE_PX: int = 20
    FIRING_PULSE_DURATION_S: float = 0.15
    FIRING_COOLDOWN_S: float = 10.0

@dataclass(frozen=True)
class KinematicsConfig:
    MAX_FORWARD_SPEED_MS: float = 2.0
    MAX_LATERAL_SPEED_MS: float = 1.5
    MAX_YAW_RATE_RDS: float = 0.6
    SCAN_YAW_RATE_RDS: float = 0.25
    LOITER_ALTITUDE_M: float = 15.0
    APPROACH_ALTITUDE_M: float = 12.0
    TAKEOFF_ALTITUDE_M: float = 8.0

@dataclass(frozen=True)
class PIDConfig:
    YAW_KP: float = 0.003
    YAW_KI: float = 0.0001
    YAW_KD: float = 0.001
    PITCH_KP: float = 0.002
    PITCH_KI: float = 0.00005
    PITCH_KD: float = 0.0008
    INTEGRAL_WINDUP_LIMIT: float = 50.0

@dataclass(frozen=True)
class TimerConfig:
    OCCLUSION_TIMEOUT_S: float = 8.0
    HEARTBEAT_INTERVAL_S: float = 0.05
    VELOCITY_RESEND_INTERVAL_S: float = 0.9
    SCAN_DWELL_S: float = 3.0

@dataclass(frozen=True)
class LogConfig:
    ENABLE_LOGGING: bool = True
    LOG_DIR: Path = BASE_DIR / "logs"

@dataclass(frozen=True)
class SafetyConfig:
    MIN_BATTERY_VOLTAGE: float = 14.2
    BATTERY_CELL_COUNT: int = 4

@dataclass(frozen=True)
class AppConfig:
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    engagement: EngagementConfig = field(default_factory=EngagementConfig)
    kinematics: KinematicsConfig = field(default_factory=KinematicsConfig)
    pid: PIDConfig = field(default_factory=PIDConfig)
    timers: TimerConfig = field(default_factory=TimerConfig)
    log: LogConfig = field(default_factory=LogConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)

CFG = AppConfig()
