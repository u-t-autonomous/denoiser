#!/usr/bin/env python
from std_msgs.msg import String, Int32
from denoising.msg import Action, Sim
import pygame
import rospy
from denoiser import Denoiser
import copy
from action_selection import init_k, det_all_k, init_probs, update_all_P
import pandas as pd
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

def determine_action_clf():
    global clf_list
    while len(clf_list) < 5:
        pass
    action = choice(clf_list)
    clf_list = []
    return action

def label_action(label):
    if label == 2:
        return 'a' 
    if label == 3:
        return 's' 
    if label == 4:
        return 'd'

def clf_callback(msg):
    global clf_list
    clf_list.append(msg.data)

def callback(msg):
    global err, log, time_steps, x_size, y_size, target, table, steps, lock_80, lock_90, lock_95, trial, trials, name, pub, new_state, target_state
    time_steps = msg.time_steps
    action_set = set(['a','s','d'])
    action = Action()    
    errors = msg.error
    if time_steps == steps:
        log = []
        trial += 1
        table['er'].append(errors)
        print '{}/{}'.format(trial, trials)
        if not lock_80:
            table['ts_80'].append(None)
            table['er_80'].append(None)
        else:
            lock_80 = False
        if not lock_90:
            table['ts_90'].append(None)
            table['er_90'].append(None)
        else:
            lock_90 = False        
        if not lock_95:
            table['ts_95'].append(None)
            table['er_95'].append(None)   
        else:
            lock_95 = False
    state = msg.state
    action_log = msg.cmd
    current_state = msg.new_state
    target_state = msg.target_state
    key_input = determine_action(current_state, target_state)
    clf_input = determine_action_clf()
    if key_input in action_set:
        action.rand = label_action(clf_input)
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

    probs = 0
    log.append([time_steps, state, action_log, probs])
    log = sorted(log, key=lambda eval: eval[0])
    log = sorted(log, key=lambda eval: eval[1])
    actions = [x for z,y,x,w in log]
    states = [y for z,y,x,w in log]
    # log = sorted(log, key=lambda eval: eval[0])
    new_log = copy.deepcopy(log)
    new_actions = denoiser.expand(actions)
    # new_actions = actions
    s = init_k(x_size, y_size)
    all_K = det_all_k(s, states, actions)
    p = init_probs(x_size, y_size)
    p = update_all_P(p, all_K)
    for i in range(len(log)):
        new_log[i][2] = new_actions[i]
    target_log.append(p[target])
    if p[target] > .80 and not lock_80:
        lock_80 = True
        table['ts_80'].append(time_steps)
        table['er_80'].append(errors)
    elif p[target] > .90 and not lock_90:
        lock_90 = True
        table['ts_90'].append(time_steps)
        table['er_90'].append(errors)
    elif p[target] > .95 and not lock_95:
        lock_95 = True
        table['ts_95'].append(time_steps)
        table['er_95'].append(errors)
    if trial == trials:
        df = pd.DataFrame(data = table)
        print df
        df.to_csv(sep = ',', path_or_buf='/home/sahabi/hasan/denoise/data/{}.csv'.format(name))
        pygame.quit()
        rospy.signal_shutdown('Because: {}'.format(trial))
    if time_steps != steps:
        pub.publish(action)


def main():
    global time_steps, steps, trials, name, pub
    trials = rospy.get_param('~trials')
    steps = rospy.get_param('~steps')
    name = rospy.get_param('~name')
    subs = rospy.Subscriber('log', Sim, callback)
    subs = rospy.Subscriber('classification', Int32, clf_callback)
    pub = rospy.Publisher('cmd', Action, queue_size=10)
    while not rospy.is_shutdown():
        pass

if __name__ == '__main__':
    clf_list = []
    trial = 1
    trials = 0
    lock_80 = False
    lock_90 = False
    lock_95 = False
    table = {'ts_80': [], 'ts_90': [], 'ts_95': [],'er_80': [], 'er_90': [], 'er_95': [], 'er': []}
    rospy.init_node('subs', anonymous=True)
    err = rospy.get_param('~err')
    beta_param = rospy.get_param('~bp')
    denoiser = Denoiser(err, beta_param, [0,1,2])
    target = (3, 0)
    x_size = 15
    y_size = 1
    log = []
    target_log = []
    time_steps = 0
    main()