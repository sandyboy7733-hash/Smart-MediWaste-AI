from ultralytics import YOLO

# Use the same segmentation task and dataset as camera_test.py.
model = YOLO("yolov8n-seg.pt")

results = model.train(
    data="dataset/MediWaste_Final/data.yaml",
    epochs=50,
    imgsz=640,
    batch=8,
    name="MediWaste_Final",
    project="runs/segment"
)

print()
print("======================================")
print("✅ Training completed")
print("======================================")
print("Your trained model will be inside:")
print("runs/segment/MediWaste_Final/weights/")
print()
print("Best model:")
print("runs/segment/MediWaste_Final/weights/best.pt")