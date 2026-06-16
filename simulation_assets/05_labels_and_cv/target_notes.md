# Target Detection Notes for TranquilShot Simulation

## Valid target criteria
- YOLO class: elephant (class 0)
- Confidence: >= 0.70
- Both range sensors within 0.5–30.0 m
- Depth variance between two ToF sensors: > 0.05 m (proves 3D target, not flat)
- Size gate: bbox height consistent with ~2.5m elephant at measured depth
- Motion gate: optical flow magnitude > 0.0 (relaxed in Gazebo sim)
- All 4 gates must pass simultaneously

## Rejection targets in simulation
- elephant_poster: flat, zero depth variance -> Gate 2 rejects
- far_elephant: valid detection but tracker selects nearest first
- Any detection below 0.70 confidence -> Gate 1 rejects

## Known model-detector pairing
- Model: ComputerVisionPipeline/runs/detect/train-6/weights/best.pt
- Trained on: YOLO format, class 0 = elephant
- If fallback mode active: synthetic detection used for pipeline testing only
- For final demo: model must load and run on real camera frames from Gazebo

## Sample frames folder
Drop 5–20 raw PNG/JPG frames here from:
- Gazebo camera topic captures
- Dataset sample images
These help verify detector is working on in-simulation imagery before the demo
