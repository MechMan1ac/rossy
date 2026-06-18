import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

import xacro

def generate_launch_description():

    pkg_dir = get_package_share_directory("rossy")

    #Launch robot state publisher
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    pkg_dir,'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'true'}.items()
    )

    gazebo_world = os.path.join(pkg_dir, "worlds", "obstacles_world.sdf.xml")

    #Launch gazebo
    gz_sim = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")
                ),
                launch_arguments={'gz_args': f'{gazebo_world} -r', 'use_sim_time': 'true'}.items(),
            )
    
    #Spawn in robot
    gz_spawn_entity = Node(
                        package="ros_gz_sim",
                        executable="create",
                        output="screen",
                        arguments=["-topic", "robot_description",
                                   "-name", "rossy",
                                    '-x', '0.0',
                                    '-y', '0.0',
                                    '-z', '0.1',])
    
    #The bridge node connects Gazebo Fortress topics to ROS 2
    gz_bridge = Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            arguments=[
                # 1. Clock: Mandatory for use_sim_time: True
                "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",

                # 2. Odometry: Brings odom data into ROS
                "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",

                # 3. TF: Bridges the coordinate transforms (Fixes Fixed Frame issue)
                "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",

                # 4. Joint States: Fixes wheel-to-base_link transforms
                "/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model",

                # 5. Cmd_Vel: Allows you to drive the robot (Bidirectional)
                "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
                
                #6. LaserScan: Brings laser data into ROS
                "/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan"
            ],
            parameters=[{
                "use_sim_time": True,
            }],
            output="screen"
        )
    
    #Diff drive control
    diff_cont_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
        parameters=[{"use_sim_time": True}]
    )

    #Joint state broadcaster
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
        parameters=[{"use_sim_time": True}]
    )

    #Rviz2
    rviz2 = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    parameters=[{'use_sim_time': True}]
)
    
    #Launch all of them!            
    return LaunchDescription([
        rsp,
        rviz2,
        gz_sim,
        gz_spawn_entity,
        gz_bridge,
        diff_cont_spawner,
        joint_broad_spawner,
    ])
