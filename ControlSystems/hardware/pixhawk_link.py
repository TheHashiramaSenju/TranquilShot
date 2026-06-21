from __future__ import annotations
import time
from pymavlink import mavutil

from config import CFG
from utils.math_helpers import clamp

class PixHawkController:
    def __init__(self):
        self.conn = mavutil.mavlink_connection(
            CFG.hardware.FC_CONNECTION_STRING,
            baud = CFG.hardware.FC_BAUD_RATE
        )
        self.conn.wait_heartbeat(timeout=CFG.hardware.FC_HEARTBEAT_TIMEOUT)
        self.boot_time = time.time()
        self.last_velocity_send = 0.0
        
    def arm_and_takeoff(self, target_altitude_m:float) -> None:
        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,1,0,0,0,0,0,0
        )
        
        time.sleep(1)
        
        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, target_altitude_m
        )
        
        self._wait_altitude(target_altitude_m * 0.92)
        
    def _wait_altitude(self, target_m: float) -> None:
        while True:
            msg = self.conn.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2)
            if msg and (msg.relative_alt / 1000.0) >= target_m:
                break
            
    def send_velocity(self, vx:float, vy:float, vz: float, yaw_rate: float) -> None:
        
        vx = clamp(vx, -CFG.kinematics.MAX_FORWARD_SPEED_MS, CFG.kinematics.MAX_FORWARD_SPEED_MS)
        vy = clamp(vy, -CFG.kinematics.MAX_LATERAL_SPEED_MS, CFG.kinematics.MAX_LATERAL_SPEED_MS)
        yaw_rate = clamp(yaw_rate, -CFG.kinematics.MAX_YAW_RATE_RDS, CFG.kinematics.MAX_YAW_RATE_RDS)
        
        self.conn.mav.set_position_target_local_ned_send(
            int((time.time() - self.boot_time) * 1000),
            self.conn.target_system,
            self.conn.target_component, 
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
            0b0000_0111_0110_0111,
            0, 0, 0,
            vx, vy, vz,
            0, 0, 0,
            0, yaw_rate
        )
        self.last_velocity_send = time.time()
    
    def hover(self) -> None:
        self.send_velocity(0.0, 0.0, 0.0, 0.0)
    
    def fire_payload(self) -> None:
        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            CFG.hardware.PAYLOAD_SERVO_CHANNEL,
            2000,
            0, 0, 0, 0, 0
        )
        time.sleep(CFG.engagement.FIRING_PULSE_DURATION_S)
        self.conn.mav.command_long_send(
            self.conn.target_system,
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            CFG.hardware.PAYLOAD_SERVO_CHANNEL,
            1000,
            0, 0, 0, 0, 0
        )
    
    def return_to_launch(self) -> None:
        self.conn.mav.command_long_send(
            self.conn.target_system, 
            self.conn.target_component,
            mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH,
            0, 0, 0, 0, 0, 0, 0, 0
        )
    
    def get_battery_voltage(self) -> float:
        msg = self.conn.recv_match(type = "SYS_STATUS", blocking = True, timeout = 1)
        if msg: 
            return msg.voltage_battery / 1000.0 
        return 99.0 
    
    def set_mode(self, mode_name: str) -> None:
        mode_id = self.conn.mode_mapping()[mode_name]
        self.conn.mav.set_mode_send(
            self.conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )

    def needs_velocity_refresh(self) -> bool:
        return (time.time() - self.last_velocity_send) >= CFG.timers.VELOCITY_RESEND_INTERVAL_S

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass