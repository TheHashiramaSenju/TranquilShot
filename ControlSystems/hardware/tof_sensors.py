# hardware/tof_sensors.py (Laptop Testing Version)
import time
from config import CFG 

class DistanceSensor:
    def __init__(self):
        print("[INIT] Laptop Depth Mode Active (Bypassing I2C VL53L1X).")
        # We hardcode 10000 mm (10 meters) so it always falls safely 
        # within your MIN (5m) and MAX (15m) firing distances.
        self.last_valid_mm : int = 10000 
    
    def get_distance_mm(self) -> int:
        """
        Simulates returning a perfect 10-meter distance measurement.
        This tricks main.py into thinking the target is safely in range.
        """
        return self.last_valid_mm
    
    def close(self) -> None:
        # Nothing to close since we aren't using physical I2C wires
        pass