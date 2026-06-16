import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from launch.substitutions import Command


def generate_launch_description():
    desc_share = get_package_share_directory('tranq_description')
    world_file = os.path.join(desc_share, 'worlds', 'elephant_field.world')
    xacro_file = os.path.join(desc_share, 'urdf', 'drone.urdf.xacro')

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        additional_env={'GZ_SIM_RESOURCE_PATH': desc_share}
    )

    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': Command(['xacro ', xacro_file])
        }]
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_ros_bridge',
        output='screen',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/range_1@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/range_2@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        parameters=[{'use_sim_time': True}],
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'tranq_drone', '-topic', 'robot_description', '-x', '0.0', '-y', '0.0', '-z', '1.2'],
        output='screen'
    )

    def cfg(pkg, file_name):
        return os.path.join(get_package_share_directory(pkg), 'config', file_name)

    nodes = [
        Node(package='tranq_detector', executable='detector_node', output='screen', parameters=[{'use_sim_time': True}, cfg('tranq_detector', 'detector_params.yaml')]),
        Node(package='tranq_fusion', executable='fusion_node', output='screen', parameters=[{'use_sim_time': True}, cfg('tranq_fusion', 'fusion_params.yaml')]),
        Node(package='tranq_tracker', executable='tracker_node', output='screen', parameters=[{'use_sim_time': True}, cfg('tranq_tracker', 'tracker_params.yaml')]),
        Node(package='tranq_controller', executable='controller_node', output='screen', parameters=[{'use_sim_time': True}, cfg('tranq_controller', 'controller_params.yaml')]),
        Node(package='tranq_actuator', executable='actuator_node', output='screen', parameters=[{'use_sim_time': True}, cfg('tranq_actuator', 'actuator_params.yaml')]),
        Node(package='tranq_visualization', executable='viz_node', output='screen', parameters=[{'use_sim_time': True}, cfg('tranq_visualization', 'viz_params.yaml')]),
    ]

    return LaunchDescription([
        gz_sim,
        robot_state_pub,
        bridge,
        TimerAction(period=3.0, actions=[spawn]),
        TimerAction(period=5.0, actions=nodes),
    ])
