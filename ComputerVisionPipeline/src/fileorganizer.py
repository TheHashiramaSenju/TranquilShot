import os 
import shutil

img_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_preprocessed/images/train"
label_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_trainer/labels"
output_dir = "/media/notshadow/d5dd988b-c393-4302-aa45-32bcfc8463c2/WorkFolder/TranquilShot/dataset_trainer/images"

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

'''
# we can also use slicing here 

filename = "image14.jpg"
# 1. Get the base name -> "image14"
base_name = os.path.splitext(filename)[0]
just_the_number = base_name[5:]
print(just_the_number)



## we can use digit filtering

filename = "frame105.jpg"
base_name = os.path.splitext(filename)[0]
just_the_number = "".join([char for char in base_name if char.isdigit])
print("Just the number")
'''

