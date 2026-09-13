from ultralytics import YOLO
import cv2

MODEL_PATH = r"C:\Users\MUKI & SACHIN\Downloads\MediWaste_AI_Sample\runs\segment\MediWaste_Final\weights\best.pt"

model = YOLO(MODEL_PATH)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("MediWaste AI Camera Started")
print("Show a glove, syringe, or bottle to the camera.")
print("Press Q to quit.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera frame.")
        break

    results = model.predict(
        source=frame,
        conf=0.25,
        device=0,
        verbose=False
    )

    annotated_frame = results[0].plot()

    cv2.imshow("MediWaste AI - YOLOv8", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()