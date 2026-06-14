from ultralytics import YOLO
import yaml


model = YOLO('yolov8n.pt')

results = model.train(
    data="data.yaml",
    epochs=100,
    patience=15,          # Slightly higher patience so it doesn't quit too early
    batch=8,
    dropout=0.2,
    
    # 1. Turn Mosaic back ON (Crucial for small datasets)
    mosaic=1.0,           
    
    # 2. Native Spatial Augmentations (Preventing memorization of object placement)
    degrees=10.0,         # Randomly rotate images by +/- 10 degrees
    translate=0.1,        # Randomly translate (shift) images by 10%
    scale=0.5,            # Randomly scale images by +/- 50%
    fliplr=0.5,           # 50% chance to flip images left-to-right
    
    # 3. Native Color/Pixel Augmentations (Replacing your Albumentations)
    hsv_h=0.015,          # Image HSV-Hue augmentation
    hsv_s=0.7,            # Image HSV-Saturation augmentation
    hsv_v=0.4,            # Image HSV-Value (brightness) augmentation
    bgr=0.2               # 20% chance to flip image channels (adds color chaos)
)