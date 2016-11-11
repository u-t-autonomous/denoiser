#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from numpy.random import choice


def randomize_input(user_input, p = 0.7):
    action_set = set(['a','s','d'])
    action_set -= set(user_input)
    options = len(action_set)
    a = [user_input, action_set.pop(), action_set.pop()]
    p = [p, (1-p)/options, (1-p)/options]
    return choice(a, p=p)


def main():
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('cmd', String, queue_size=10)
    rate = rospy.Rate(10) # 10hz
    action_set = set(['a','s','d'])
    while not rospy.is_shutdown():
        key_input = raw_input("What's your move? ")
        if key_input in action_set:
            action = randomize_input(key_input)
            if action == 'a':
                action = 'west'
            elif action == 'd':
                action = 'east'
            elif action == 's':
                action = 'stay'
            print action
            pub.publish(action)
        rate.sleep()

if __name__ == '__main__':
	main()