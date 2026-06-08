import os
import shutil
import glob

def run_mini_sync():
    # 1. Get the absolute path to your project root folder
    # This ensures the script works perfectly no matter where you execute it from
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(src_dir, ".."))
    
    # 2. Map absolute paths to your folders
    mini_labels_dir = os.path.join(project_root, "dataset_processed_mini", "labels")
    target_lbl_dir = os.path.join(project_root, "dataset_temp", "labels", "train")
    
    # Ensure the destination folder exists
    os.makedirs(target_lbl_dir, exist_ok=True)

    # 3. Locate all your downloaded DagsHub text files
    downloaded_labels = glob.glob(os.path.join(mini_labels_dir, "*.txt"))
    print(f"Scanning source: {mini_labels_dir}")
    print(f"Found {len(downloaded_labels)} exported label text files inside mini folder.")

    paired_count = 0

    for label_path in downloaded_labels:
        full_label_name = os.path.basename(label_path)
        
        # Skip the generic classes file if it exists
        if full_label_name == "classes.txt":
            continue
        
        # Example: '00573502__frame_000064.txt' -> 'frame_000064.txt'
        if "__" in full_label_name:
            original_base_name = full_label_name.split("__")[1]
        else:
            original_base_name = full_label_name
            
        destination_label_path = os.path.join(target_lbl_dir, original_base_name)

        shutil.copy(label_path, destination_label_path)
        paired_count += 1

    print(f"\n Sync Matrix Complete!")
    print(f"Successfully paired and moved {paired_count} clean text labels into 'dataset_temp/labels/train/'.")

if __name__ == "__main__":
    run_mini_sync()
