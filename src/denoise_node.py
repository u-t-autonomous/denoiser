#!/usr/bin/env python
from std_msgs.msg import String
from denoising.msg import Sim
import pygame
import rospy
from denoiser import Denoiser
import copy

def callback(msg):
    global log, time_step
    time_step += 1
    state = msg.state
    ev = msg.cmd
    log.append([time_step, state, ev])
    log = sorted(log, key=lambda eval: eval[0])
    log = sorted(log, key=lambda eval: eval[1])
    evals = [x for z,y,x in log]
    # log = sorted(log, key=lambda eval: eval[0])
    new_log = copy.deepcopy(log)
    new_evals = denoiser.swap(evals)
    for i in range(len(log)):
        new_log[i][2] = new_evals[i]

def main():
    global time_step
    rospy.init_node('subs', anonymous=True)
    subs = rospy.Subscriber('log', Sim, callback)
    steps = rospy.get_param('~steps')
    while time_step < steps and not rospy.is_shutdown():
        pass


if __name__ == '__main__':
    denoiser = Denoiser(.3, .5, [0,1,2])
    log = []
    time_step = 0
    main()
