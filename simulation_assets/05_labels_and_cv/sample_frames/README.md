# Sample frames folder
Drop 5–20 PNG or JPG images here from:
- Gazebo camera topic: ros2 run image_view image_view --ros-args -r image:=/camera/image_raw
- Or use: ros2 bag record /camera/image_raw and extract frames

These are used to verify that your trained best.pt model detects the simulation geometry.
If it does not detect the Gazebo elephant mesh, you need either:
  1. Domain adaptation (render extra Gazebo frames and add to training set)
  2. Or lower confidence threshold temporarily for demo

Naming: frame_001.png, frame_002.png, etc.
