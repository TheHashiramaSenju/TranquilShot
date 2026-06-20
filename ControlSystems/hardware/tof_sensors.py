import VL53L1X
from config import CFG 

class DistanceSensor:
    def __init__(self):
        self.tof = VL53L1X.VL53L1X(
            i2c_bus = CFG.hardware.TOF_I2C_BUS,
            i2c_address = CFG.hardware.TOF_I2C_ADDRESS
        )
        
        self.tof.open()
        self.tof.set_timing(
            CFG.hardware.TOF_TIMING_BUDGET_MS * 1000,
            CFG.hardware.TOF_TIMING_BUDGET_MS
        )
        
        self.tof.start_ranging(2)
        self.last_valid_mm : int = 0 
    
    def get_distance_mm(self) -> int:
        try:
            raw = self.tof.get_distance()
            if raw > 0:
                self.last_valid_mm = raw
            return self.last_valid_mm
        except OSError:
            return self.last_valid_mm
    
    def close(self) -> None:
        try :
            self.tof.stop_ranging()
            self.tof.close()
        except Exception:
            pass 