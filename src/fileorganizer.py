import os 
import shutil

img_dir = "../dataset_preprocessed"
label_dir = "../dataset_trainer/labels"
output_dir = "../dataset_trainer/images"

os.makedirs(output_dir, exist_ok=True)

label_basenames = set()
for root, dirs, files in os.walk(label_dir):
    for filename in files:
        name_without_ext, _ = os.path.splitext(filename)
        label_basenames.add(name_without_ext)

matched_images = []

for root, dirs, files in os.walk(img_dir):
    for filename in files:
        img_name_without_ext, _ = os.path.splitext(filename)
        
        if img_name_without_ext in label_basenames:
            full_img_path = os.path.join(root, filename)
            matched_images.append(full_img_path)
            
            # Optional: Copies the matched image to your new "images" directory
            shutil.copy(full_img_path, os.path.join(output_dir, filename))

print(f"Found and processed {len(matched_images)} matching images.")
