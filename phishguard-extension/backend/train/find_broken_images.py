# backend/train/find_broken_images.py

from PIL import Image, ImageFile
import os

# Allow PIL to load truncated & partially corrupted images
ImageFile.LOAD_TRUNCATED_IMAGES = True

ROOT = "datasets"   # Inside backend/train folder

broken_files = []

for cls in os.listdir(ROOT):
    class_path = os.path.join(ROOT, cls)

    if not os.path.isdir(class_path):
        continue

    for filename in os.listdir(class_path):
        file_path = os.path.join(class_path, filename)

        try:
            img = Image.open(file_path)
            img.load()  # Force full read

        except Exception as e:
            print("❌ BROKEN:", file_path, "Error:", e)
            broken_files.append(file_path)

print("\n--------------------------------------")
print("Total Broken Images:", len(broken_files))
print("--------------------------------------")

for f in broken_files:
    print(f)
