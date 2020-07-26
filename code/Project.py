#!/usr/bin/env python

## waypoint following demo that obtains current position from
## amcl_pose & navigates to waypoints sequentially

import rospy
import math
from math import pi
import serial
from time import time, sleep
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import MapMetaData, OccupancyGrid
from tf.transformations import euler_from_quaternion


console_ser = serial.Serial(port = "/dev/ttyACM0",baudrate=115200)

# obtain waypoints from the rviz selection & split the x,y values from the waypoint file pointed in the open command


wp_x, wp_y = [], []
with open(file, "rw") as f:
	for line in f:
		wp_x.append(line.split(',')[0])
		wp_y.append(line.split(',')[1])
print(len(wp_x))  # check the no of waypoints


# create a class to encapsulate various sub-routines required for the program
class Control(object):
	# intialize the variables
	def __init__(self):
		self.poses_x = 0.0  # x position from AMCL
		self.poses_y = 0.0  # y position from AMCL
		self.theta_car = 0.0  # theta from AMCL
		self.steer = 0  # required steer for the rally car
		self.acc = 0  # required gas for the rally car
		self.err = 0.0  # error in the orientation from current position to the waypoint
		self.prev_err = 0.0  # Previous error to use for derivative controller
		self.current_wp = 0  # Iterator for current waypoint
		self.dist_rem = 0.0  # distance remaining
		self.prev_dist_rem = 0.0  # previous distance remaining for d-controller
		self.Kp = 1500  # proportional gain for steer
		self.Kd = 800  # derivative controller gain for steer
		self.kpa = 300  # proportional gain for gas
		self.kda = 300  # derivative controller gain for gas
		self.check_feed = [] # check camera feed
		rospy.on_shutdown(self.sht_dwn)  # rospy shutdown hook

	# amcl_pose to get current position
	def amclCallback(self, data):
		self.poses_x = data.pose.pose.position.x
		self.poses_y = data.pose.pose.position.y
		(_, _, self.theta_car) = euler_from_quaternion(
			[data.pose.pose.orientation.x, data.pose.pose.orientation.y, data.pose.pose.orientation.z,
			 data.pose.pose.orientation.w])



	def controller(self):
		global wp_x, wp_y

		rospy.init_node('amclListener', anonymous=True)
		rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.amclCallback)
		counter = 0
		rate = rospy.Rate(100)
		while not rospy.is_shutdown():
			x_diff = float(wp_x[self.current_wp]) - self.poses_x  # calculate error in x
			y_diff = float(wp_y[self.current_wp]) - self.poses_y  # calculate error in y
			theta_wp = math.atan2(y_diff, x_diff)  # calculate car based on these error
			self.err = self.theta_car - theta_wp  # alpha	(required angle to make)
			print("amcl_x = ", self.poses_x, "amcl_y =", self.poses_y)  # Printing amcl_x, amcl_y for check
			print(x_diff, y_diff)  # printing x, y
			print('error =', self.err)  # printing error

			# adjusting error direction when more than 180 deg
			if self.err > pi:
				self.err = -2 * pi + self.err
			elif self.err < -pi:
				self.err = 2 * pi + self.err

			# controller design with steer
			self.steer = int(self.Kp * (self.err) + self.Kd * (self.prev_err - self.err))

			# bounding the error to max value for serial input
			if self.steer > 2048:
				self.steer = 2048
			elif self.steer < -2048:
				self.steer = -2048

			# calculate the distance remaining
			self.dist_rem = math.sqrt((x_diff) ** 2 + (y_diff) ** 2)
			self.acc = int(self.kpa * self.dist_rem + self.kda * (self.prev_dist_rem - self.dist_rem))
			# self.acc = int(250 + 10*self.dist_rem)

			# bound the max gas value
			if self.acc > 200:
				self.acc = 200
			elif self.acc < 0:
				self.acc = 0

			# if the distance is less reduce the gas value to slow down
			if self.dist_rem < 0.5:
				self.acc = 80

			# write the required command to the serial port
			console_ser.write('A' + '%+05d' % self.steer + '%+05d' % self.acc)
			print('command = ', 'A' + '%+05d' % self.steer + '%+05d' % self.acc)

			# update the waypoint at 10Hz and not when the last waypoint and distance remaining is less than 1.5
			if counter % 10 == 0 and self.current_wp != (len(wp_x) - 1) and self.dist_rem < 1.5:
				self.current_wp = self.current_wp + 1

			# write serial command to stop the car at the last waypoint
			if self.current_wp == (len(wp_x) - 1) and self.dist_rem < 0.2:
				console_ser.write('A+0000+0000')

			self.prev_err = self.err  # set current error as previous error
			self.prev_dist_rem = self.dist_rem  # set current distance remaining as previous distance remaining
			print('current_wp = ', self.current_wp)  # print the current waypoint
			print('\n')
			rate.sleep()
		rospy.spin()  # spin to loop

	def sht_dwn(self):  # write serial command to stop the car when shutdown is called (ctrl+c)
		for i in range(100):
			console_ser.write('A+0000+0000')


def main(x,y,w,h,file):
	con = Control()  # create object for the class
	con.controller()  # call the method controller()
