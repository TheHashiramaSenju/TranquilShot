import csv
import time
from pathlib import Path
from dataclasses import dataclass, fields, astuple
from config import CFG


@dataclass
class FlightRecord:
    timestamp: float
    state: str
    target_x: int
    target_y: int
    confidence: float
    distance_mm: int
    yaw_cmd: float
    pitch_cmd: float
    vx_cmd: float
    battery_v: float
    fired: bool


class FlightLogger:
    def __init__(self):
        if not CFG.log.ENABLE_LOGGING:
            self._writer = None
            self._file = None
            return

        CFG.log.LOG_DIR.mkdir(parents=True, exist_ok=True)
        filename = CFG.log.LOG_DIR / f"flight_{int(time.time())}.csv"
        self._file = open(filename, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow([f.name for f in fields(FlightRecord)])

    def write(self, record: FlightRecord) -> None:
        if self._writer is None:
            return
        self._writer.writerow(astuple(record))
        self._file.flush()

    def close(self) -> None:
        if self._file and not self._file.closed:
            self._file.close()
