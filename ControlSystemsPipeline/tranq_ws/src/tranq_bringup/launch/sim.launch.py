import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    desc_share = get_package_share_directory('tranq_description')
    world_file = os.path.join(desc_share, 'worlds', 'elephant_field.world')

    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
        additional_env={'GZ_SIM_RESOURCE_PATH': desc_share}
    )

    gz_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_ros_bridge',
        output='screen',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/range_1@sensor_msgs/msg/Range@gz.msgs.LaserScan',
            '/range_2@sensor_msgs/msg/Range@gz.msgs.LaserScan',
            '/drone/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
        ],
        parameters=[{'use_sim_time': True}]
    )

    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': open(
                os.path.join(desc_share, 'urdf', 'drone.urdf.xacro')
            ).read()
        }]
    )

    def cfg(pkg):
        return os.path.join(
            get_package_share_directory(pkg), 'config',
            pkg.replace('tranq_', '') + '_params.yaml'
        )

    def make_node(pkg, exe, params_file):
        return Node(package=pkg, executable=exe, name=exe,
                    output='screen',
                    parameters=[{'use_sim_time': True}, params_file])

    delayed_nodes = TimerAction(period=3.0, actions=[
        make_node('tranq_detector',   'detector_node',   cfg('tranq_detector')),
        make_node('tranq_fusion',     'fusion_node',     cfg('tranq_fusion')),
        make_node('tranq_tracker',    'tracker_node',    cfg('tranq_tracker')),
        make_node('tranq_controller', 'controller_node', cfg('tranq_controller')),
        make_node('tranq_actuator',   'actuator_node',   cfg('tranq_actuator')),
    ])

    return LaunchDescription([
        gz_sim,
        gz_ros_bridge,
        robot_state_pub,
        delayed_nodes,
    ])
