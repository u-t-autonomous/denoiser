#!/usr/bin/env python
from environment import Simulation
from std_msgs.msg import String
from denoising.msg import Sim
import pygame
import rospy

def callback(msg):
    global pubs
    state = sim.get_state()
    done, s = sim.move([msg.data])
    log = Sim()
    if msg.data == 'west':
        log.cmd = 0
    elif msg.data == 'stay':
        log.cmd = 1
    elif msg.data == 'east':
        log.cmd = 2
    log.state = state['agents'][0][0]
    pubs.publish(log)


def main():
    global pubs
    rospy.init_node('subs', anonymous=True)
    subs = rospy.Subscriber('cmd', String, callback)
    pubs = rospy.Publisher('log', Sim, queue_size=10)
    done = False
    while not rospy.is_shutdown():
        pass


if __name__ == '__main__':
    sim = Simulation("/home/sahabi/catkin_ws/src/denoising/src/config.txt") # absolute path is better
    main()
