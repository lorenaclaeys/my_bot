import sys
import rclpy
from rclpy.duration import Duration
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

class robot_action_client(Node):
	def __init__(self):
		super().__init__('traj_action_client')
		self.action_client = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller/folow_joint_trajectory')
	
	def send_goal(self, angle):
		goal_msg = FollowJointTrajectory.Goal()
		
		joint_names = ['joint_xy', 'joint_zx', 'joint_needle', 'link_2_aux_joint', 'link_2_joint', 'link_3_aux_joint', 'link_3_joint', 'link_4_aux_joint', 'link_4_joint', 'link_5_aux_joint', 'link_5_joint']
		
		points = []
		point1 = JointTrajectoryPoint()
		point1.positions = [0.0] * len(joint_names) #start
		
		point2 = JointTrajectoryPoint()
		point2.time_from_start = Duration(seconds=1, nanoseconds=0).to_msg()
		point2.positions = [angle] * len(joint_names) #end
		
		points.append(point1)
		points.append(point2)
		
		goal_msg.goal_time_tolerance = Duration( seconds=1, nanoseconds=0).to_msg()
		goal_msg.trajectory.joint_names = joint_names
		goal_msg.trajectory.points = points
		
		self.action_client.wait_for_server()
		self.send_goal_future = self.action_client.send_goal_async(goal_msg, feedback_callback= self.feedback_callback)
		self._send_goal_future.add_done_callback(self.goal_response_callback)
		
	def get_response_callback(self, future):
		goal_handle = future.result()
		if not goal_handle.accepted:
			self.get_logger().info('Goal rejected :(')
		return
		
		self.get_logger().info('Goal accepted :)')
		
		self._get_result_future = goal_handle.get_result_async()
		self._get_result_future.add_done_callback = (self.get_result_callback)
		
	def get_result_callback(self, future):
		result = future.result().result
		self.get_logger().info('Result :' + str(result)) 
		rclpy.shutdown()
		
	def feedback_callback(self, feedback_msg):
		feedback = feedback_msg.feedback
		#self.get_logger().info('received feedback: '+ str(feedback))
		
def main(arg=None):
	rclpy.init()
	action_client = robot_action_client()
	angle = float(sys.argv[1])
	future = action_client.send_goal(angle)
	rclpy.spin(action_client)
	
if __name__ == '__main__':
	main()
	




		
		
		
