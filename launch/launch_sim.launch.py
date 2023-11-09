import os
from posixpath import join
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import ExecuteProcess
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")   
    package_name="my_bot" 
    controller_params = os.path.join(get_package_share_directory("my_bot"), "config","controller.yaml")

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),"launch","rsp.launch.py"
                )]), launch_arguments={"use_sim_time": "true"}.items()
    )

    # Include the Gazebo launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py")]),
             )

    # Run the spawner node from the gazebo_ros package
    spawn_entity = Node(package="gazebo_ros", executable="spawn_entity.py",
            arguments=["-topic", "robot_description",
                        "-entity", "my_bot"],
            output="screen")
          
    joint_state_pub = Node(package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_publisher",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}])

    ctrl = Node(package="controller_manager",
            executable="ros2_control_node",
            parameters=[{"robot_description": "robot"}, controller_params])

    robot_controller_spawner = Node(package="controller_manager",
            executable="spawner",
            arguments=["joint_trajectory_controller", "-c", "/controller_manager"])
            
    joint_state_broadcaster_spawner = Node(package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"])

    # Launch them all!
    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        joint_state_pub,
        ctrl,
        joint_state_broadcaster_spawner,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[robot_controller_spawner],
            )
        ),
    ])
   
