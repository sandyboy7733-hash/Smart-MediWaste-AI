import cv2
import os
import time

# ==============================
# MediWaste AI Dataset Capture
# ==============================

CLASS_NAME = input(
    "Enter class name (glove/syringe/cotton/medicine_bottle): "
).strip().lower()

SAVE_DIR = os.path.join("dataset", "raw", CLASS_NAME)

os.makedirs(SAVE_DIR, exist_ok=True)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Camera could not be opened")
    exit()

print()
print("======================================")
print(" MediWaste AI - Dataset Capture")
print("======================================")
print(f"Class: {CLASS_NAME}")
print(f"Saving to: {SAVE_DIR}")
print()
print("SPACE  → Capture image")
print("Q      → Quit")
print("======================================")

image_count = len(os.listdir(SAVE_DIR))

while True:

    success, frame = camera.read()

    if not success:
        print("❌ Failed to read camera frame")
        break

    display_frame = frame.copy()

    cv2.putText(
        display_frame,
        f"Class: {CLASS_NAME}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    cv2.putText(
        display_frame,
        f"Images: {image_count}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        display_frame,
        "SPACE = Capture | Q = Quit",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.imshow(
        "MediWaste AI - Dataset Capture",
        display_frame
    )

    key = cv2.waitKey(1) & 0xFF

    # Capture
    if key == 32:

        filename = os.path.join(
            SAVE_DIR,
            f"{CLASS_NAME}_{image_count:04d}.jpg"
        )

        cv2.imwrite(filename, frame)

        image_count += 1

        print(f"✅ Saved: {filename}")

        # Small delay to avoid accidental multiple captures
        time.sleep(0.2)

    # Quit
    elif key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print()
print("🛑 Dataset capture stopped")
print(f"Total images: {image_count}")