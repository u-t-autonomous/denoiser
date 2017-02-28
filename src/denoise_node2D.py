#!/usr/bin/env python
from std_msgs.msg import String, Int32
from denoising.msg import Action, Sim
import pygame
import rospy
from denoiser import Denoiser
import copy
from action_selection import init_k, det_all_k_2D, init_probs, update_all_P
import pandas as pd
from numpy.random import choice
action_map = {'a':'west','s':'stay','d':'east','w':'north','x':'south'}

def randomize_input(user_input, prob = 0.7):
    action_set = set(['a','s','d','x','w'])
    action_set -= set(user_input)
    options = len(action_set)
    a = [user_input, action_set.pop(), action_set.pop(), action_set.pop(), action_set.pop()]
    p = [prob, (1-prob)/options, (1-prob)/options, (1-prob)/options, (1-prob)/options]
    return choice(a, p=p)

def determine_action(current_state, target_state):
    if current_state > target_state:
        return 'a'
    if current_state < target_state:
        return 'd'
    if current_state == target_state:
        return 's' 

def determine_action_2D(current_xstate,current_ystate, target_xstate, target_ystate):
    candidate = []
    if current_xstate > target_xstate:
        candidate.append('a')
    elif current_xstate < target_xstate:
        candidate.append('d')
    elif current_xstate == target_xstate and current_ystate == target_ystate:
        candidate.append('s') 
    if current_ystate > target_ystate:
        candidate.append('w')
    if current_ystate < target_ystate:
        candidate.append('x')
    return choice(candidate)
      

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
    global action_map, err, log, time_steps, x_size, y_size, target, table, steps, lock_80, lock_90, lock_95, trial, trials, name, pub, new_state, target_state
    time_steps = msg.time_steps
    action_set = set(['a','s','d','w','x'])
    action = Action()    
    errors = msg.error 


    xstate = msg.xstate
    ystate = msg.ystate
    action_log = msg.cmd
    current_xstate = msg.new_xstate
    target_xstate = msg.target_xstate
    current_ystate = msg.new_ystate
    target_ystate = msg.target_ystate    
    key_input = determine_action_2D(current_xstate,current_ystate, target_xstate, target_ystate)

    #clf_input = determine_action_clf()
    if key_input in action_set:
        #action.rand = label_action(clf_input)
        action.rand = randomize_input(key_input, 1 - err)
        action.rand = action_map[action.rand]
        key_input = action_map[key_input]
        action.true = key_input

    probs = 0
    log.append([time_steps, xstate, ystate, action_log, probs])
    log = sorted(log, key=lambda eval: eval[0])
    log = sorted(log, key=lambda eval: eval[1])
    actions = [x for z,y,m,x,w in log]
    xstates = [y for z,y,m,x,w in log]
    ystates = [m for z,y,m,x,w in log]
    # log = sorted(log, key=lambda eval: eval[0])
    new_log = copy.deepcopy(log)
    #new_actions = denoiser.expand(actions)
    new_actions = denoiser.swap(actions)
    #new_actions = actions
    s = init_k(x_size, y_size)
    all_K = det_all_k_2D(s, xstates, ystates, new_actions)
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
    if p[target] > .95:
        action.done = True       
    if time_steps == steps or action.done:
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
    name = name + '_2D'
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
    denoiser = Denoiser(err, beta_param, [0,1,2,3,4])
    target = (3, 3)
    x_size = 10
    y_size = 10
    log = []
    target_log = []
    time_steps = 0
    main()