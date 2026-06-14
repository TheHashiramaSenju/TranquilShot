from ultralytics import YOLO
model_path = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/runs/detect/train/weights/best.pt"
save_path = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/autoannotatelogs"
model = YOLO(model_path)

train_results = model.predict(
    source = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/annotation_dataset/images/train",
    save = True,
    save_txt = True,
    conf = 0.25,
    device = 0,  #for GPU
    
    project = save_path,
    name = 'Run1_training',
    exist_ok = True
)

val_results = model.predict(
    source = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/annotation_dataset/images/val",
    save = True,
    save_txt = True,
    conf = 0.25,
    device = 0,  #for GPU
    
    project = save_path,
    name = 'Run1_validation',
    exist_ok = True
)

