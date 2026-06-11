import os

from launch import LaunchDescription
from launch_ros.actions import SetParameter, Node
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

from ament_index_python.packages import get_package_share_directory

import xacro

def generate_launch_description():

    pkg_dir = get_package_share_directory("rossy")
    xacro_file = os.path.join(pkg_dir, "description", "robot.xacro")
    robot_desc = xacro.process_file(xacro_file)
    robot_desc_xml = robot_desc.toxml()

    #Robot state publisher
    rsp = Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{"use_sim_time": False, "robot_description": robot_desc_xml}]
        )

    controller_params_file = os.path.join(pkg_dir,'config','my_controllers.yaml')
    
    #Controller manager
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_desc_xml}, 
                    controller_params_file],
    )

    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    #Diff drive control
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    #Joint state broadcaster
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )
    
    #Launch all of them!            
    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
    ])
