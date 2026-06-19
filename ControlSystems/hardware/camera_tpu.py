from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
import cv2

from pycoral.utils.dataset import read_label_file
from pycoral.utils.elephant import make_interpreter
from pycoral.adapters import common, detect 


from config import CFG

@dataclass
class Detection:
    cx : int 
    cy : int
    confidence : float
    bbox_w : int
    bbox_h : int
    

class TPUDetector:
    def __init__(self):
        self.labels = read_label_file(str(CFG.vision.LABELS_PATH))
        self.interpreter = make_interpreter(str(CFG.vision.MODEL_PATH))
        self.interpreter.allocate_tensors()
        self.input_size = common.input_size(self.interpreter)
        
        self.cap = cv2.VideoCapture(CFG.hardware.CAMERA_INDEX)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"The camera cannot be opened {CFG.hardware.CAMERA_INDEX}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CFG.vision.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CFG.vision.FRAME_HEIGHT)
        self.target_label = CFG.vision.TARGET_LABEL.lower()
        
    def detect_target(self) -> Optional[Detection]:
        ret, frame = self.cap.read()
        if not ret  :
            return None
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, self.input_size)
        common.set_input(self.interpreter, resized)
        self.interpreter.invoke()
        
        objs = detect.get_objects(
            self.interpreter,
            score_threshold=CFG.vision.CONFIDENCE_THRESHOLD
        )
        
        best: Optional[detect.Object] = None ###
        for obj in objs :
            label = self.labels.get(obj.id, "").lower()
            if label != self.target_label:
                continue
            if best is None or obj.score > best.score:
                best = obj
                
        if best is None:
            return None 
        
        scale_x = CFG.vision.FRAME_WIDTH / self.input_size[0]
        scale_y = CFG.vision.FRAME_HEIGHT / self.input_size[0]
        
        x0 = int(best.bbox.xmin * scale_x)
        y0 = int(best.bbox.ymin * scale_y)
        x1 = int(best.bbox.xmax * scale_x)
        y1 = int(best.bbox.ymax * scale_y)
        
        return Detection(
            cx=(x0 + x1) // 2,
            cy = (y0 + y1) // 2,
            confidence  = float(best.score), 
            bbox_w=x1 - x0,
            bbox_h=y1 - y0
        )

    def close(self) -> None:
        if self._cap.isOpened():
            self._cap.release()