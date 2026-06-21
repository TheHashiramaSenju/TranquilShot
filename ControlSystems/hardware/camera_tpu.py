import cv2
from ultralytics import YOLO
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
        print("[INIT] Laptop Vision Mode Active (Using YOLO & best.pt).")
        # Load your original PyTorch model for the laptop test
        # We temporarily point this to best.pt instead of the tflite model
        model_path = str(CFG.vision.MODEL_PATH).replace('target_edgetpu.tflite', 'best.pt')
        self.model = YOLO(model_path) 
        
        
        self.cap = cv2.VideoCapture(CFG.hardware.CAMERA_INDEX)

    def detect_target(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        # 1. Run the AI on the live webcam frame
        results = self.model(frame, verbose=False, device='cpu')
        
        # 2. Show the webcam feed with the AI's bounding boxes drawn on it!
        annotated_frame = results[0].plot()
        cv2.imshow("Drone AI View", annotated_frame)
        cv2.waitKey(1)

        # 3. Parse the results to find our target
        best_target = None
        
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            label = self.model.names[class_id].lower()
            confidence = float(box.conf[0])

            # Is it an elephant? Is it confident enough?
            if label == CFG.vision.TARGET_LABEL and confidence >= CFG.vision.CONFIDENCE_THRESHOLD:
                
                # Get bounding box coordinates and calculate the exact center pixel
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                
                # If there are multiple elephants, lock onto the most confident one
                if best_target is None or confidence > best_target.confidence:
                    best_target = Detection(label, confidence, cx, cy)

        # Send the exact coordinates back to main.py
        return best_target

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()