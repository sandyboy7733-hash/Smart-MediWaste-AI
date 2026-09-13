import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("best.pt")

# Open laptop camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Camera could not be opened")
    exit()

print("✅ Camera started")
print("✅ YOLO model loaded")
print("📷 Reading camera frames...")
print("Press Q to quit")

while True:

    # Read camera frame
    success, frame = camera.read()

    if not success:
        print("❌ Failed to read camera frame")
        break

    # Send frame to YOLO
    results = model(
        frame,
        conf=0.85,
        verbose=False
    )

    # Get YOLO annotated frame
    annotated_frame = results[0].plot()

    # Print detections
    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            confidence = float(box.conf[0])

            print(
                f"🎯 Detected: {class_name} | "
                f"Confidence: {confidence * 100:.2f}%"
            )

    # Show result
    cv2.imshow(
        "MediWaste AI - YOLO Detection",
        annotated_frame
    )

    # Quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()

print("🛑 Camera stopped")