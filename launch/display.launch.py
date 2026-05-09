import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource

import xacro

def generate_launch_description():

    pkg_dir = get_package_share_directory('my_robot_project')
    xacro_file = os.path.join(pkg_dir, 'description', 'main_robot_urdf.xacro')
    robot_desc = xacro.process_file(xacro_file)
        

    gz_sim = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
                ),
                launch_arguments={'gz_args': 'empty.sdf -r'}.items(),
            )
    
    gz_spawn_entity = Node(
                        package='ros_gz_sim',
                        executable='create',
                        output='screen',
                        arguments=['-topic', 'robot_description',
                                   '-name', 'rossy',
                                    '-x', '0.0',
                                    '-y', '0.0',
                                    '-z', '0.1',])
                            
    return LaunchDescription([
      #Launch rviz
        Node(
            package='rviz2',
            executable='rviz2',
            parameters=[{'use_sim_time': True}],
            output='screen',
        ),

        #Launch robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'use_sim_time': True, 'robot_description': robot_desc.toxml()}]
        ),

        #Launch joint state publisher gui
        # Node(
        #     package='joint_state_publisher_gui',
        #     executable='joint_state_publisher_gui',
        #     name='my_joint_gui'
        # ),

        #Launch joint state publisher
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            parameters=[{'use_sim_time': True}]
        ),


        # The bridge node connects Gazebo Fortress topics to ROS 2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                # 1. Clock: Mandatory for use_sim_time: True
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',

                # 2. Odometry: Brings odom data into ROS
                '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',

                # 3. TF: Bridges the coordinate transforms (Fixes Fixed Frame issue)
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',

                # 4. Joint States: Fixes wheel-to-base_link transforms
                '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',

                # 5. Cmd_Vel: Allows you to drive the robot (Bidirectional)
                '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist'
            ],
            output='screen'
        ),


        #Launch gazebo
        gz_sim,

        #Spawn in robot
        gz_spawn_entity
    ])

