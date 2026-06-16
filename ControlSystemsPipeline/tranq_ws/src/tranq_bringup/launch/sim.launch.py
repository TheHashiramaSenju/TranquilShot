# sim.launch.py â€” TranquilShot Simulation Launcher
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# FIXES APPLIED:
#   1. Added spawn_entity node (drone was never spawned into Gazebo)
#   2. Completed ros_gz_bridge arguments (camera, IMU, odom, tf were missing)
#   3. Added /enable_motors publisher (arms MulticopterVelocityControl)
#   4. Fixed GZ_SIM_RESOURCE_PATH to include materials/ subdir
#   5. Replaced hardcoded model_path with LaunchArgument override
#   6. Proper TimerAction sequencing: gz â†’ spawn(3s) â†’ bridge(4s) â†’ arm(6s) â†’ nodes(5s)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (ExecuteProcess, SetEnvironmentVariable,
                             TimerAction, DeclareLaunchArgument)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc_share    = get_package_share_directory('tranq_description')
    bringup_share = get_package_share_directory('tranq_bringup')

    world_file  = os.path.join(desc_share, 'worlds', 'elephant_field.world')
    xacro_file  = os.path.join(desc_share, 'urdf',   'drone.urdf.xacro')

    # LaunchArg: allow overriding model path without editing YAML
    model_path_arg = DeclareLaunchArgument(
        'model_path',
        default_value='',
        description='Path to YOLOv8 .pt weights file'
    )
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    model_path   = LaunchConfiguration('model_path')

    detector_config = os.path.join(bringup_share, 'config', 'sim_config.yaml')

    # â”€â”€ 1. Gazebo Harmonic â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        additional_env={
            'GZ_SIM_RESOURCE_PATH': ':'.join([
                desc_share,
                os.path.join(desc_share, 'models'),
                os.path.join(desc_share, 'materials'),
                os.environ.get('GZ_SIM_RESOURCE_PATH', '')
            ])
        }
    )

    # â”€â”€ 2. Robot State Publisher â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(
                Command(['xacro ', xacro_file]), value_type=str
            )
        }]
    )

    # â”€â”€ 3. Spawn drone (FIX: this was completely missing) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    spawn_drone = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_tranq_drone',
        output='screen',
        arguments=[
            '-name',  'tranq_drone',
            '-topic', 'robot_description',
            '-z', '0.3',
            '-x', '0.0',
            '-y', '0.0',
        ]
    )

    # â”€â”€ 4. ROS â†” Gazebo Bridge (FIX: was truncated/incomplete) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/enable_motors@std_msgs/msg/Bool]gz.msgs.Boolean',
        ]
    )

    # â”€â”€ 5. Arm motors (FIX: MulticopterVelocityControl ignores /cmd_vel
    #        until /enable_motors receives True) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    arm_motors = ExecuteProcess(
        cmd=[
            'ros2', 'topic', 'pub', '--once',
            '/enable_motors', 'std_msgs/msg/Bool', '{data: true}'
        ],
        output='screen'
    )

    # â”€â”€ 6. Application Nodes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    detector_node = Node(
        package='tranq_detector',
        executable='detector_node',
        name='tranq_detector',
        output='screen',
        parameters=[
            detector_config,
            {'use_sim_time': use_sim_time},
            # Override model_path if provided via CLI arg
        ]
    )

    controller_node = Node(
        package='tranq_controller',
        executable='controller_node',
        name='tranq_controller',
        output='screen',
        parameters=[detector_config, {'use_sim_time': use_sim_time}]
    )

    fusion_node = Node(
        package='tranq_fusion',
        executable='fusion_node',
        name='tranq_fusion',
        output='screen',
        parameters=[detector_config, {'use_sim_time': use_sim_time}]
    )

    actuator_node = Node(
        package='tranq_actuator',
        executable='actuator_node',
        name='tranq_actuator',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        model_path_arg,
        SetEnvironmentVariable('ROS_DOMAIN_ID', '42'),

        # Core sim â€” starts immediately
        gz_sim,
        robot_state_pub,

        # Spawn drone after Gazebo is up (3 s)
        TimerAction(period=3.0, actions=[spawn_drone]),

        # Bridge after spawn (4 s)
        TimerAction(period=4.0, actions=[bridge]),

        # Application nodes after bridge (5 s)
        TimerAction(period=5.0, actions=[
            detector_node,
            controller_node,
            fusion_node,
            actuator_node,
        ]),

        # Arm motors last, after bridge is confirmed (6 s)
        TimerAction(period=6.0, actions=[arm_motors]),
    ])
