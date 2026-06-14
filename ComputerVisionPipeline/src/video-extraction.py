import os
import glob
import cv2

def slice_videos(video_dir, output_dir, train_ratio=0.8, target_fps=3):
    image_train_dir = os.path.join(output_dir, "images", "train")
    image_val_dir = os.path.join(output_dir, "images", "val")
    label_train_dir = os.path.join(output_dir, "labels", "train")
    label_val_dir = os.path.join(output_dir, "labels", "val")

    for folder in [image_train_dir, image_val_dir, label_train_dir, label_val_dir]:
        os.makedirs(folder, exist_ok=True)

    video_files = sorted(glob.glob(os.path.join(video_dir, "*.mp4")))
    if not video_files:
        print(f"Error: No .mp4 files found in {video_dir}")
        return

    split_index = int(len(video_files) * train_ratio)
    train_videos = video_files[:split_index]

    global_frame_count = 0

    for video_path in video_files:
        is_train = video_path in train_videos
        target_img_dir = image_train_dir if is_train else image_val_dir
        
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        
        if video_fps == 0:
            print(f"Skipping corrupt video: {video_path}")
            continue

        frame_interval = max(1, int(video_fps / target_fps))
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                global_frame_count += 1
                img_name = f"frame_{global_frame_count:06d}.jpg"
                out_path = os.path.join(target_img_dir, img_name)
                cv2.imwrite(out_path, frame)

            frame_idx += 1

        cap.release()
    
    print(f"Pipeline executed successfully. Processed {global_frame_count} total frames.")

if __name__ == "__main__":
    slice_videos(
        video_dir="../dataset_raw",
        output_dir="../dataset_preprocessed",
        train_ratio=0.8,
        target_fps=3
    )
