import os
import shutil
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE = Path(r"C:\Users\MUKI & SACHIN\Downloads\MediWaste_AI_Sample")

OLD_DATASET = BASE / "dataset" / "MediWaste_Final"
NEW_DATASET = BASE / "dataset" / "MediWaste_Detection"

NEW_GLOVE = Path(
    r"C:\Users\MUKI & SACHIN\Downloads\Gloves.v2-test-2.yolov8"
)

# Existing classes
# 0 = Glove
# 1 = Syringe
# 2 = Bottle

# ============================================================
# IMAGE EXTENSIONS
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp", ".webp"
}

# ============================================================
# CREATE DIRECTORIES
# ============================================================

for split in ["train", "valid", "test"]:
    (NEW_DATASET / split / "images").mkdir(parents=True, exist_ok=True)
    (NEW_DATASET / split / "labels").mkdir(parents=True, exist_ok=True)

# ============================================================
# CONVERT SEGMENTATION -> DETECTION
# ============================================================

def polygon_to_box(coords):
    """
    YOLO segmentation:
    x1 y1 x2 y2 x3 y3 ...

    Convert to:
    x_center y_center width height
    """

    xs = coords[0::2]
    ys = coords[1::2]

    if not xs or not ys:
        return None

    xmin = max(0.0, min(xs))
    xmax = min(1.0, max(xs))
    ymin = max(0.0, min(ys))
    ymax = min(1.0, max(ys))

    width = xmax - xmin
    height = ymax - ymin

    if width <= 0 or height <= 0:
        return None

    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2

    return x_center, y_center, width, height


def convert_existing_split(split):
    image_dir = OLD_DATASET / split / "images"
    label_dir = OLD_DATASET / split / "labels"

    output_image_dir = NEW_DATASET / split / "images"
    output_label_dir = NEW_DATASET / split / "labels"

    if not image_dir.exists():
        print(f"[WARNING] Missing image folder: {image_dir}")
        return

    if not label_dir.exists():
        print(f"[WARNING] Missing label folder: {label_dir}")
        return

    count = 0

    for image in image_dir.iterdir():

        if image.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        old_label = label_dir / f"{image.stem}.txt"

        if not old_label.exists():
            print(f"[WARNING] No label: {image.name}")
            continue

        new_image = output_image_dir / image.name
        new_label = output_label_dir / f"{image.stem}.txt"

        # Copy image
        shutil.copy2(image, new_image)

        detection_lines = []

        with open(old_label, "r", encoding="utf-8") as f:

            for line in f:
                parts = line.strip().split()

                if len(parts) < 7:
                    continue

                try:
                    class_id = int(parts[0])
                    coords = list(map(float, parts[1:]))

                    # Existing classes are already correct:
                    # 0 Glove
                    # 1 Syringe
                    # 2 Bottle

                    box = polygon_to_box(coords)

                    if box is None:
                        continue

                    x, y, w, h = box

                    detection_lines.append(
                        f"{class_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
                    )

                except ValueError:
                    continue

        with open(new_label, "w", encoding="utf-8") as f:
            f.write("\n".join(detection_lines))

        count += 1

    print(f"[OK] Converted {count} {split} images")


# ============================================================
# COPY/CONVERT EXISTING DATASET
# ============================================================

print("\n==============================================")
print("CONVERTING EXISTING MEDIWASTE DATASET")
print("==============================================\n")

for split in ["train", "valid", "test"]:
    convert_existing_split(split)


# ============================================================
# ADD NEW GLOVE DATASET
# ============================================================

print("\n==============================================")
print("ADDING NEW GLOVE DATASET")
print("==============================================\n")


def add_new_glove_split(split):
    image_dir = NEW_GLOVE / split / "images"
    label_dir = NEW_GLOVE / split / "labels"

    if not image_dir.exists() or not label_dir.exists():
        print(f"[WARNING] Missing Glove {split} folders")
        return

    output_image_dir = NEW_DATASET / split / "images"
    output_label_dir = NEW_DATASET / split / "labels"

    added = 0

    for image in image_dir.iterdir():

        if image.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        old_label = label_dir / f"{image.stem}.txt"

        if not old_label.exists():
            continue

        glove_lines = []

        with open(old_label, "r", encoding="utf-8") as f:

            for line in f:
                parts = line.strip().split()

                if len(parts) != 5:
                    continue

                try:
                    class_id = int(parts[0])

                    # New dataset:
                    # 1 = Glove
                    #
                    # Final dataset:
                    # 0 = Glove

                    if class_id != 1:
                        continue

                    x = float(parts[1])
                    y = float(parts[2])
                    w = float(parts[3])
                    h = float(parts[4])

                    glove_lines.append(
                        f"0 {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
                    )

                except ValueError:
                    continue

        # Only copy images that actually contain a Glove
        if not glove_lines:
            continue

        # Prefix avoids filename collisions
        new_name = f"newglove_{image.name}"
        new_label_name = f"newglove_{image.stem}.txt"

        shutil.copy2(
            image,
            output_image_dir / new_name
        )

        with open(
            output_label_dir / new_label_name,
            "w",
            encoding="utf-8"
        ) as f:
            f.write("\n".join(glove_lines))

        added += 1

    print(f"[OK] Added {added} new Glove images to {split}")


# New Glove dataset split mapping
add_new_glove_split("train")
add_new_glove_split("valid")
add_new_glove_split("test")


# ============================================================
# CREATE DATA.YAML
# ============================================================

yaml_content = f"""path: {NEW_DATASET.as_posix()}

train: train/images
val: valid/images
test: test/images

nc: 3

names:
  0: Glove
  1: Syringe
  2: Bottle
"""

with open(NEW_DATASET / "data.yaml", "w", encoding="utf-8") as f:
    f.write(yaml_content)


# ============================================================
# SUMMARY
# ============================================================

print("\n==============================================")
print("DATASET CREATION COMPLETE")
print("==============================================")

print(f"\nNew dataset:")
print(NEW_DATASET)

print("\nClasses:")
print("0 = Glove")
print("1 = Syringe")
print("2 = Bottle")

print("\nOriginal dataset was NOT modified.")

print("\nNext step: inspect the dataset counts before training.")