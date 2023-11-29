import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # Define the 'use_sim_time' launch configuration variable
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # Get the path to the 'my_bot' package and the xacro files
    pkg_path = get_package_share_directory('my_bot')
    xacro_file_robot = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    

    # Process the xacro files into URDF descriptions
    robot_description_config = xacro.process_file(xacro_file_robot)
 
    # Create the robot_state_publisher nodes with the necessary parameters
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_config.toxml(),
                     'use_sim_time': use_sim_time}],
    )


    # Define the launch description with a declaration for 'use_sim_time'
    # and the robot_state_publisher nodes
    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='false',
            description='Flag to enable use_sim_time'
        ),
        node_robot_state_publisher,
    ])


