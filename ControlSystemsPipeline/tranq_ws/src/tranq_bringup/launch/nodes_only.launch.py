import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    def cfg(pkg):
        return os.path.join(get_package_share_directory(pkg), 'config',
                            pkg.replace('tranq_', '') + '_params.yaml')

    def make_node(pkg, exe, params_file):
        return Node(package=pkg, executable=exe, name=exe,
                    output='screen', parameters=[params_file])

    return LaunchDescription([
        make_node('tranq_detector',   'detector_node',   cfg('tranq_detector')),
        make_node('tranq_fusion',     'fusion_node',     cfg('tranq_fusion')),
        make_node('tranq_tracker',    'tracker_node',    cfg('tranq_tracker')),
        make_node('tranq_controller', 'controller_node', cfg('tranq_controller')),
        make_node('tranq_actuator',   'actuator_node',   cfg('tranq_actuator')),
    ])
