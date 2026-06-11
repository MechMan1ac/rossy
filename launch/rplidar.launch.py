import os

from launch_ros.actions import Node
from launch import LaunchDescription


def generate_launch_description():
    
    return LaunchDescription([
        Node(
            package="rplidar_ros",
            executable="rplidar_composition",
            output="screen",
            parameters=[{'channel_type': 'serial',
                        'serial_port': '/dev/serial/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.4:1.0-port0',
                        'frame_id': 'laser_frame',
                        'scan_mode': 'Standard',
                        'inverted': False,
                        'angle_compensate': True,
                        'serial_baudrate': 115200}]
        )
    ])
