import cv2
import time
from config import CFG
from dataclasses import dataclass

@dataclass
class Detection:
    label: str
    confidence: float
    center_x: int
    center_y: int

class TPUDetector:
    def __init__(self):
        print("[INIT] Laptop Vision Mode Active (Bypassing PyCoral).")
        # Turn on the laptop webcam
        self.cap = cv2.VideoCapture(CFG.hardware.CAMERA_INDEX)
        self.mock_frame_counter = 0

    def detect_target(self):
        """
        Since we don't have the Coral chip on the laptop, 
        we will simulate a target moving across the screen to test the flight math.
        """
        ret, frame = self.cap.read()
        if not ret:
            return None

        # Show the webcam feed on your screen so you can see it working
        cv2.imshow("Drone Camera Feed", frame)
        cv2.waitKey(1)

        self.mock_frame_counter += 1
        
        # Simulate an elephant appearing after 50 frames (about 2 seconds)
        if self.mock_frame_counter > 50 and self.mock_frame_counter < 300:
            # Simulate the elephant starting on the right side of the screen (X=500)
            # and slowly moving toward the center (X=320)
            simulated_x = 500 - ((self.mock_frame_counter - 50) * 0.5)
            
            return Detection(
                label=CFG.vision.TARGET_LABEL,
                confidence=0.88,
                center_x=int(simulated_x),
                center_y=CFG.vision.CENTER_Y
            )
        
        return None

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()