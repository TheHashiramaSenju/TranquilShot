from ultralytics import YOLO
model = YOLO('yolo11n.pt')

results = model.train(
    data='../data.yaml',
    epochs=40,
    imgsz=640,
    batch=16,
    name='yolo11n_tranquilshot'
)