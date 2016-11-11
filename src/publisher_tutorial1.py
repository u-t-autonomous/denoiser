#!/usr/bin/env python
import rospy
from std_msgs.msg import String

# create a node
# publish your command to /cmd

def get_input():
	key_input = raw_input("What's your move? ")
	
	return key_input

def main():
	rospy.init_node('talker', anonymous=True)
	pub = rospy.Publisher('cmd', String, queue_size=10)
	rate = rospy.Rate(10) # 10hz
	while not rospy.is_shutdown():
		command = get_input()
		pub.publish(command)
		rate.sleep()

if __name__ == '__main__':
    main()