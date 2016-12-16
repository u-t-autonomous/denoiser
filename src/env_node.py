#!/usr/bin/env python
from environment import Simulation
from std_msgs.msg import String
from denoising.msg import Sim, Action
import pygame
import rospy
import action_selection
from time import sleep

def callback(msg):
    global pubs, time_steps, sim, num_error, trial, trials
    state = sim.get_state()
    time_steps += 1
    log = Sim()
    log.state = state['agents'][0][0]
    done, s = sim.move([msg.rand])
    state = sim.get_state()
    log.new_state = state['agents'][0][0]
    if msg.rand == 'west':
        log.cmd = 0
    elif msg.rand == 'stay':
        log.cmd = 1
    elif msg.rand == 'east':
        log.cmd = 2
    log.target_state = 3
    log.time_steps = time_steps
    if msg.true != msg.rand:
        num_error += 1
    error = num_error/float(time_steps)
    log.error = error   
    pubs.publish(log)
    if trial == trials:
        rospy.signal_shutdown('Because: {}'.format(trial))


def main():
    global pubs, time_steps, sim, num_error, trials, trial
    rospy.init_node('subs', anonymous=True)
    steps = rospy.get_param('~steps')
    trials = rospy.get_param('~trials')
    subs = rospy.Subscriber('cmd', Action, callback)
    pubs = rospy.Publisher('log', Sim, queue_size=10)
    log = Sim()
    state = sim.get_state()
    log.state = state['agents'][0][0]
    sleep(1)
    pubs.publish(log)

    done = False
    while not rospy.is_shutdown():
        if time_steps == steps:
            subs.unregister()
            trial += 1
            time_steps = 0
            num_error = 0
            sim = Simulation("/home/sahabi/catkin_ws/src/denoising/src/config.txt") # absolute path is better            
            sleep(.2)
            subs = rospy.Subscriber('cmd', Action, callback)
            log = Sim()
            state = sim.get_state()
            log.state = state['agents'][0][0]
            sleep(1)
            pubs.publish(log)
        else:
            pass


if __name__ == '__main__':
    time_steps = 0
    num_error = 0
    trial = 1
    sim = Simulation("/home/sahabi/catkin_ws/src/denoising/src/config.txt") # absolute path is better
    main()
