from ultralytics import YOLO
import cv2

# Load your model
model = YOLO(r"D:\CODING\object detection\best.pt")  # path to your .pt file

# Open laptop camera (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame")
        break

    # Run inference
    results = model(frame, verbose=False)

    # Draw results on frame
    annotated_frame = results[0].plot()

    cv2.imshow("Object Detection - Press 'q' to quit", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()