#!/usr/bin/env python
from environment import Simulation
from std_msgs.msg import String
from denoising.msg import Sim, Action
import pygame
import rospy
import action_selection
from time import sleep

def callback(msg):
    global pubs, time_steps, sim, num_error, trial, trials, done
    steps = rospy.get_param('steps')
    print 'in env ', steps
    state = sim.get_state()
    time_steps += 1
    log = Sim()
    log.xstate = state['agents'][0][0]
    log.ystate = state['agents'][0][1]
    done, s = sim.move([msg.rand])
    if msg.done:
        done = msg.done
    state = sim.get_state()
    log.new_xstate = state['agents'][0][0]
    log.new_ystate = state['agents'][0][1]
    if msg.rand == 'west':
        log.cmd = 0
    elif msg.rand == 'stay':
        log.cmd = 1
    elif msg.rand == 'east':
        log.cmd = 2
    elif msg.rand == 'north':
        log.cmd = 3
    elif msg.rand == 'west':
        log.cmd = 4
    log.target_xstate = 3
    log.target_ystate = 3
    log.time_steps = time_steps
    if msg.true != msg.rand:
        num_error += 1
    error = num_error/float(time_steps)
    log.error = error   
    pubs.publish(log)
    if trial == trials:
        rospy.signal_shutdown('Because: {}'.format(trial))


def main():
    global pubs, time_steps, sim, num_error, trials, trial, done
    rospy.init_node('subs', anonymous=True)
    #steps = rospy.get_param('~steps')
    trials = rospy.get_param('~trials')
    subs = rospy.Subscriber('cmd', Action, callback)
    pubs = rospy.Publisher('log', Sim, queue_size=10)
    log = Sim()
    state = sim.get_state()
    log.xstate = state['agents'][0][0]
    log.ystate = state['agents'][0][1]
    sleep(1)
    pubs.publish(log)

    done = False
    while not rospy.is_shutdown():
        #print 'while: ', done
        steps = rospy.get_param('steps')
        if time_steps == steps or done:
            done = False
            subs.unregister()
            trial += 1
            time_steps = 0
            num_error = 0
            sim = Simulation("/home/sahabi/catkin_ws/src/denoising/src/config_2D.txt", viz=False) # absolute path is better            
            sleep(.2)
            subs = rospy.Subscriber('cmd', Action, callback)
            log = Sim()
            state = sim.get_state()
            log.xstate = state['agents'][0][0]
            log.ystate = state['agents'][0][1]
            sleep(1) # was 1 second
            pubs.publish(log)
        else:
            pass


if __name__ == '__main__':
    time_steps = 0
    num_error = 0
    trial = 1
    sim = Simulation("/home/sahabi/catkin_ws/src/denoising/src/config_2D.txt", viz=False) # absolute path is better
    main()
