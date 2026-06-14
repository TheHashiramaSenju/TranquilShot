'''
This filecleaner runs after the filemover function has run. It checks for any inconsistencies in the 
images and labels and deletes any files that don't have a match. 
This ensures that the training process won't run into issues with missing labels or images.



import os 
import shutil 

train_img_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/images/train"
val_img_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/images/val"
train_label_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/labels/train"
val_label_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/labels/val"
void_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/void_dir"

label_basenames = set()

for root, dirs, files in os.walk(train_img_dir):
    for filename in files:
        img_name_without_ext, _ = os.path.splitext(filename)
        label_basenames.add(img_name_without_ext)

unmatched_labels = []

for root, dirs, files in os.walk(train_label_dir):
    for filename in files:
        label_name_without_ext, _ = os.path.splitext(filename)
        unmatched_labels.append(label_name_without_ext)
        if label_name_without_ext not in label_basenames:
            full_label_path = os.path.join(root, filename) 
            unmatched_labels.append(full_label_path)
            shutil.copy(full_label_path, os.path.join(void_dir, filename))
            
            



# Find unmatched labels
unmatched_labels = label_basenames - set(matched_labels)

# Delete unmatched label files
for label_basename in unmatched_labels:
    for label_dir in [train_label_dir, val_label_dir]:
        label_path = os.path.join(label_dir, f"{label_basename}.txt")
        if os.path.exists(label_path):
            os.remove(label_path)   

'''

import os 
import shutil 

train_img_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/images/train"
val_img_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/images/val"
train_label_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/labels/train"
val_label_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/labels/val"
void_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/void_dir"

os.makedirs(void_dir, exist_ok=True)

def quarantine_mismatches(img_dir, label_dir):
    if not os.path.exists(img_dir) or not os.path.exists(label_dir):
        return

    images = {os.path.splitext(f)[0]: f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))}
    labels = {os.path.splitext(f)[0]: f for f in os.listdir(label_dir) if f.endswith('.txt') and os.path.isfile(os.path.join(label_dir, f))}

    for base_name, img_file in images.items():
        if base_name not in labels:
            src_path = os.path.join(img_dir, img_file)
            dest_path = os.path.join(void_dir, img_file)
            shutil.move(src_path, dest_path)
            print(f"Quarantined unmatched image: {img_file}")

    for base_name, label_file in labels.items():
        if base_name not in images:
            src_path = os.path.join(label_dir, label_file)
            dest_path = os.path.join(void_dir, label_file)
            shutil.move(src_path, dest_path)
            print(f"Quarantined unmatched label: {label_file}")

quarantine_mismatches(train_img_dir, train_label_dir)
quarantine_mismatches(val_img_dir, val_label_dir)