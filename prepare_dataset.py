import os
import shutil
import random
from pathlib import Path

# ============================================================
# MEDIWASTE AI - FINAL DATASET PREPARATION
# YOLOv8 SEGMENTATION DATASET
#
# Classes:
#   0 = Glove
#   1 = Syringe
#   2 = Bottle
#
# This script automatically detects:
#   - YOLO detection labels: class xc yc w h
#   - YOLO segmentation labels: class x1 y1 x2 y2 ...
#
# Detection boxes are converted into rectangle polygons.
# ============================================================


# ============================================================
# 1. SOURCE DATASET PATHS
# ============================================================

GLOVE_DIR = Path(
    r"C:\Users\MUKI & SACHIN\Downloads\My First Project.yolov8"
)

SYRINGE_DIR = Path(
    r"C:\Users\MUKI & SACHIN\Downloads\Syringe"
)

BOTTLE_DIR = Path(
    r"C:\Users\MUKI & SACHIN\Downloads\plastic_bottles"
)


# ============================================================
# 2. FINAL OUTPUT PATH
# ============================================================

OUTPUT_DIR = Path(
    r"C:\Users\MUKI & SACHIN\Downloads\MediWaste_AI_Sample\dataset\MediWaste_Final"
)


# ============================================================
# 3. RANDOM SEED
# ============================================================

random.seed(42)


# ============================================================
# 4. CLASS IDs
# ============================================================

GLOVE_CLASS = 0
SYRINGE_CLASS = 1
BOTTLE_CLASS = 2


# ============================================================
# 5. IMAGE EXTENSIONS
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


# ============================================================
# 6. CREATE FINAL DATASET FOLDERS
# ============================================================

print()
print("=" * 60)
print("MEDIWASTE AI DATASET PREPARATION")
print("=" * 60)
print()

print("Removing old final dataset if it exists...")

if OUTPUT_DIR.exists():
    shutil.rmtree(OUTPUT_DIR)

print("Creating new dataset folders...")

for split in ["train", "valid", "test"]:
    (OUTPUT_DIR / split / "images").mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / split / "labels").mkdir(parents=True, exist_ok=True)

print("Folder structure created.")
print()


# ============================================================
# 7. HELPER: FIND IMAGE-LABEL PAIRS
# ============================================================

def find_pairs(images_dir, labels_dir):

    pairs = []

    if not images_dir.exists():
        print(f"WARNING: Image folder not found: {images_dir}")
        return pairs

    if not labels_dir.exists():
        print(f"WARNING: Label folder not found: {labels_dir}")
        return pairs

    for image_path in images_dir.iterdir():

        if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        label_path = labels_dir / (image_path.stem + ".txt")

        if label_path.exists():
            pairs.append((image_path, label_path))

    return pairs


# ============================================================
# 8. HELPER: CONVERT LABEL TO SEGMENTATION
# ============================================================

def convert_label_line(line, new_class_id):
    """
    Automatically detects YOLO detection or segmentation.

    Detection:
        class xc yc width height

    Segmentation:
        class x1 y1 x2 y2 x3 y3 ...

    Returns:
        converted segmentation line
        OR None if invalid
    """

    line = line.strip()

    if not line:
        return None

    parts = line.split()

    # Need at least:
    # class + 4 coordinates
    if len(parts) < 5:
        return None

    try:
        old_class = int(float(parts[0]))
        values = [float(x) for x in parts[1:]]
    except ValueError:
        return None

    # --------------------------------------------------------
    # DETECTION FORMAT
    # class xc yc width height
    # Total parts = 5
    # --------------------------------------------------------

    if len(values) == 4:

        xc = values[0]
        yc = values[1]
        width = values[2]
        height = values[3]

        # Validate normalized values
        if not (
            0 <= xc <= 1
            and 0 <= yc <= 1
            and 0 < width <= 1
            and 0 < height <= 1
        ):
            return None

        # Convert bounding box to rectangle polygon
        x1 = xc - width / 2
        y1 = yc - height / 2

        x2 = xc + width / 2
        y2 = yc + height / 2

        # Clamp values to 0-1
        x1 = max(0.0, min(1.0, x1))
        y1 = max(0.0, min(1.0, y1))

        x2 = max(0.0, min(1.0, x2))
        y2 = max(0.0, min(1.0, y2))

        polygon = [
            x1, y1,
            x2, y1,
            x2, y2,
            x1, y2
        ]

        polygon_text = " ".join(f"{v:.6f}" for v in polygon)

        return f"{new_class_id} {polygon_text}", "BOX"

    # --------------------------------------------------------
    # SEGMENTATION FORMAT
    #
    # class x1 y1 x2 y2 x3 y3 ...
    #
    # Must have an even number of coordinates.
    # Minimum 3 points = 6 coordinates.
    # --------------------------------------------------------

    if len(values) >= 6 and len(values) % 2 == 0:

        # Validate every coordinate
        for value in values:

            if value < 0 or value > 1:
                return None

        polygon_text = " ".join(f"{v:.6f}" for v in values)

        return f"{new_class_id} {polygon_text}", "SEGMENT"

    return None


# ============================================================
# 9. HELPER: PROCESS ONE DATASET
# ============================================================

def process_dataset(
    dataset_name,
    dataset_dir,
    new_class_id,
    split_mode="existing"
):

    print()
    print("-" * 60)
    print(f"PROCESSING {dataset_name.upper()} DATASET")
    print("-" * 60)

    statistics = {
        "pairs": 0,
        "box_labels": 0,
        "segment_labels": 0,
        "invalid_labels": 0,
        "empty_labels": 0,
        "images_copied": 0
    }

    # --------------------------------------------------------
    # GLOVE
    #
    # Original dataset has:
    # train/images
    # train/labels
    #
    # We split it 80 / 10 / 10
    # --------------------------------------------------------

    if split_mode == "glove":

        images_dir = dataset_dir / "train" / "images"
        labels_dir = dataset_dir / "train" / "labels"

        pairs = find_pairs(images_dir, labels_dir)

        random.shuffle(pairs)

        total = len(pairs)

        train_count = int(total * 0.80)
        valid_count = int(total * 0.10)

        train_pairs = pairs[:train_count]

        valid_pairs = pairs[
            train_count:train_count + valid_count
        ]

        test_pairs = pairs[
            train_count + valid_count:
        ]

        split_pairs = {
            "train": train_pairs,
            "valid": valid_pairs,
            "test": test_pairs
        }

    # --------------------------------------------------------
    # SYRINGE / BOTTLE
    #
    # Preserve original splits
    # --------------------------------------------------------

    else:

        split_pairs = {}

        for split in ["train", "valid", "test"]:

            images_dir = dataset_dir / split / "images"
            labels_dir = dataset_dir / split / "labels"

            split_pairs[split] = find_pairs(
                images_dir,
                labels_dir
            )

    # --------------------------------------------------------
    # PROCESS EACH SPLIT
    # --------------------------------------------------------

    for split, pairs in split_pairs.items():

        print()
        print(
            f"{dataset_name} {split}: {len(pairs)} pairs"
        )

        for image_path, label_path in pairs:

            statistics["pairs"] += 1

            # ------------------------------------------------
            # New unique filename
            # ------------------------------------------------

            prefix = dataset_name.lower()

            new_image_name = (
                f"{prefix}_{image_path.name}"
            )

            new_label_name = (
                f"{prefix}_{label_path.stem}.txt"
            )

            output_image = (
                OUTPUT_DIR
                / split
                / "images"
                / new_image_name
            )

            output_label = (
                OUTPUT_DIR
                / split
                / "labels"
                / new_label_name
            )

            # ------------------------------------------------
            # Read original label
            # ------------------------------------------------

            try:

                with open(
                    label_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    lines = f.readlines()

            except Exception as e:

                print(
                    f"ERROR reading label: {label_path}"
                )

                print(e)

                statistics["invalid_labels"] += 1

                continue

            converted_lines = []

            # ------------------------------------------------
            # Convert every label line
            # ------------------------------------------------

            for line in lines:

                if not line.strip():
                    continue

                result = convert_label_line(
                    line,
                    new_class_id
                )

                if result is None:

                    statistics["invalid_labels"] += 1

                    print(
                        f"WARNING: Invalid label skipped:"
                    )

                    print(f"  {label_path}")
                    print(f"  {line.strip()}")

                    continue

                converted_line, label_type = result

                converted_lines.append(
                    converted_line
                )

                if label_type == "BOX":
                    statistics["box_labels"] += 1

                elif label_type == "SEGMENT":
                    statistics["segment_labels"] += 1

            # ------------------------------------------------
            # Skip completely empty labels
            # ------------------------------------------------

            if len(converted_lines) == 0:

                statistics["empty_labels"] += 1

                print(
                    f"WARNING: No valid labels:"
                )

                print(f"  {label_path}")

                continue

            # ------------------------------------------------
            # Copy image
            # ------------------------------------------------

            shutil.copy2(
                image_path,
                output_image
            )

            statistics["images_copied"] += 1

            # ------------------------------------------------
            # Write converted segmentation label
            # ------------------------------------------------

            with open(
                output_label,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    "\n".join(converted_lines)
                    + "\n"
                )

    return statistics


# ============================================================
# 10. PROCESS GLOVE
# ============================================================

glove_stats = process_dataset(
    "Glove",
    GLOVE_DIR,
    GLOVE_CLASS,
    split_mode="glove"
)


# ============================================================
# 11. PROCESS SYRINGE
# ============================================================

syringe_stats = process_dataset(
    "Syringe",
    SYRINGE_DIR,
    SYRINGE_CLASS,
    split_mode="existing"
)


# ============================================================
# 12. PROCESS BOTTLE
# ============================================================

bottle_stats = process_dataset(
    "Bottle",
    BOTTLE_DIR,
    BOTTLE_CLASS,
    split_mode="existing"
)


# ============================================================
# 13. CREATE data.yaml
# ============================================================

print()
print("-" * 60)
print("CREATING data.yaml")
print("-" * 60)

yaml_path = OUTPUT_DIR / "data.yaml"

yaml_content = f"""path: {OUTPUT_DIR.as_posix()}

train: train/images
val: valid/images
test: test/images

nc: 3

names:
  0: Glove
  1: Syringe
  2: Bottle
"""

with open(
    yaml_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(yaml_content)

print(f"Created: {yaml_path}")


# ============================================================
# 14. COUNT FINAL DATASET
# ============================================================

def count_files(folder):

    if not folder.exists():
        return 0

    return len([
        f
        for f in folder.iterdir()
        if f.is_file()
        and f.suffix.lower() in IMAGE_EXTENSIONS
    ])


def count_labels(folder):

    if not folder.exists():
        return 0

    return len([
        f
        for f in folder.iterdir()
        if f.is_file()
        and f.suffix.lower() == ".txt"
    ])


print()
print("=" * 60)
print("FINAL DATASET")
print("=" * 60)

all_good = True

for split in ["train", "valid", "test"]:

    image_count = count_files(
        OUTPUT_DIR / split / "images"
    )

    label_count = count_labels(
        OUTPUT_DIR / split / "labels"
    )

    print()
    print(split.upper())
    print(f"Images : {image_count}")
    print(f"Labels : {label_count}")

    if image_count != label_count:

        print("WARNING: Images and labels do NOT match!")

        all_good = False

    else:

        print("Status : OK")


# ============================================================
# 15. PRINT CONVERSION STATISTICS
# ============================================================

print()
print("=" * 60)
print("LABEL CONVERSION STATISTICS")
print("=" * 60)

def print_stats(name, stats):

    print()
    print(name)

    print(f"  Image-label pairs : {stats['pairs']}")
    print(f"  Images copied     : {stats['images_copied']}")
    print(f"  Box labels        : {stats['box_labels']}")
    print(f"  Segment labels    : {stats['segment_labels']}")
    print(f"  Invalid labels    : {stats['invalid_labels']}")
    print(f"  Empty labels      : {stats['empty_labels']}")


print_stats("GLOVE", glove_stats)
print_stats("SYRINGE", syringe_stats)
print_stats("BOTTLE", bottle_stats)


# ============================================================
# 16. VERIFY FINAL LABEL FORMAT
# ============================================================

print()
print("=" * 60)
print("VERIFYING FINAL SEGMENTATION LABELS")
print("=" * 60)

bad_final_labels = []

for split in ["train", "valid", "test"]:

    labels_dir = (
        OUTPUT_DIR
        / split
        / "labels"
    )

    for label_file in labels_dir.glob("*.txt"):

        try:

            with open(
                label_file,
                "r",
                encoding="utf-8"
            ) as f:

                lines = f.readlines()

            for line_number, line in enumerate(lines, 1):

                parts = line.strip().split()

                if not parts:
                    continue

                # Segmentation must have:
                # class + at least 6 coordinates
                # and an even number of coordinates

                if len(parts) < 7:

                    bad_final_labels.append(
                        (
                            label_file,
                            line_number,
                            "Too few coordinates"
                        )
                    )

                    continue

                coordinate_count = len(parts) - 1

                if coordinate_count % 2 != 0:

                    bad_final_labels.append(
                        (
                            label_file,
                            line_number,
                            "Odd number of coordinates"
                        )
                    )

                    continue

                class_id = int(parts[0])

                if class_id not in [0, 1, 2]:

                    bad_final_labels.append(
                        (
                            label_file,
                            line_number,
                            "Invalid class ID"
                        )
                    )

        except Exception as e:

            bad_final_labels.append(
                (
                    label_file,
                    0,
                    str(e)
                )
            )


if len(bad_final_labels) == 0:

    print()
    print("ALL FINAL LABELS ARE VALID SEGMENTATION LABELS.")

else:

    print()
    print(
        f"WARNING: {len(bad_final_labels)} problems found."
    )

    for item in bad_final_labels[:20]:

        print(
            f"{item[0]} | line {item[1]} | {item[2]}"
        )


# ============================================================
# 17. FINAL RESULT
# ============================================================

print()
print("=" * 60)

if all_good and len(bad_final_labels) == 0:

    print("DATASET PREPARATION COMPLETED SUCCESSFULLY")
    print()
    print("All images have matching labels.")
    print("All labels use YOLO segmentation format.")
    print()
    print("Classes:")
    print("  0 = Glove")
    print("  1 = Syringe")
    print("  2 = Bottle")
    print()
    print(f"Dataset:")
    print(OUTPUT_DIR)
    print()
    print(f"YAML:")
    print(yaml_path)

else:

    print("DATASET CREATED WITH WARNINGS")
    print()
    print("Check the warnings above before training.")

print("=" * 60)
print()

