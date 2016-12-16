#!/usr/bin/env python
import rospy
from denoising.msg import Action, Sim
from numpy.random import choice

def randomize_input(user_input, prob = 0.7):
    action_set = set(['a','s','d'])
    action_set -= set(user_input)
    options = len(action_set)
    a = [user_input, action_set.pop(), action_set.pop()]
    p = [prob, (1-prob)/options, (1-prob)/options]
    return choice(a, p=p)

def determine_action(current_state, target_state):
    if current_state > target_state:
        return 'a'
    if current_state < target_state:
        return 'd'
    if current_state == target_state:
        return 's'        

def callback(msg):
    global target_state, state, time_steps, new_state
    target_state = msg.target_state
    state = msg.state
    new_state = msg.new_state
    time_steps = msg.time_steps

def main():
    global target_state, state, time_steps, new_state
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('cmd', Action, queue_size=10)
    sub = rospy.Subscriber('log', Sim, callback)
    steps = rospy.get_param('~steps')
    rate = rospy.Rate(10) # 10hz
    action_set = set(['a','s','d'])
    action = Action()
    while not rospy.is_shutdown():
        if time_steps == steps:
            state = 8
        current_state = new_state
        target_state = target_state
        key_input = determine_action(current_state, target_state)
        # key_input = raw_input("What's your move? ")
        if key_input in action_set:
            action.rand = randomize_input(key_input)
            if action.rand == 'a':
                action.rand = 'west'
            elif action.rand == 'd':
                action.rand = 'east'
            elif action.rand == 's':
                action.rand = 'stay'
            if key_input == 'a':
                key_input = 'west'
            elif key_input == 'd':
                key_input = 'east'
            elif key_input == 's':
                key_input = 'stay'
            action.true = key_input
            pub.publish(action)
        rate.sleep()

if __name__ == '__main__':
    new_state = 8
    time_steps = 0
    target_state = 3
    state = 8
    main()