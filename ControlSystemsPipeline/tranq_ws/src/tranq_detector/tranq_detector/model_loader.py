import os
from typing import List, NamedTuple
import numpy as np

class RawDetection(NamedTuple):
    conf: float
    class_id: int
    bbox_x: float
    bbox_y: float
    bbox_w: float
    bbox_h: float

class ModelLoader:
    def __init__(self, model_path: str, backend: str, target_class_id: int, conf_thresh: float):
        self._model_path = os.path.expanduser(model_path)
        self._backend = backend
        self._target_class_id = target_class_id
        self._conf_thresh = conf_thresh
        self._model = None
        if not os.path.isfile(self._model_path):
            raise FileNotFoundError(
                f"Model not found: {self._model_path}\n"
                f"Expected: ComputerVisionPipeline/runs/detect/train-6/weights/best.pt"
            )
        self._load()

    def _load(self):
        if self._backend == 'ultralytics':
            from ultralytics import YOLO
            self._model = YOLO(self._model_path)
        elif self._backend == 'ncnn':
            import ncnn
            self._model = ncnn.Net()
            self._model.load_param(self._model_path + '.param')
            self._model.load_model(self._model_path + '.bin')
        else:
            raise ValueError(f'Unknown backend: {self._backend}')

    def infer(self, frame: np.ndarray) -> List[RawDetection]:
        if self._backend == 'ultralytics':
            results = self._model(frame, conf=self._conf_thresh, verbose=False)
            detections = []
            for box in results[0].boxes:
                cls = int(box.cls[0])
                if cls != self._target_class_id:
                    continue
                conf = float(box.conf[0])
                x, y, w, h = box.xywh[0].tolist()
                detections.append(RawDetection(conf, cls, x - w / 2, y - h / 2, w, h))
            return detections
        return []
