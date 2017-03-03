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
    global action_map, err, log, time_steps, x_size, y_size, target, table, steps, lock_80,\
     lock_90, lock_95, lock_80c, lock_90c, lock_95c, trial, trials, name, pub, new_state, target_state
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
        action.rand = randomize_input(key_input, 1 - .4)
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
    new_actions = denoiser.swap(copy.deepcopy(actions))
    #new_actions = actions
    s = init_k(x_size, y_size)
    all_K = det_all_k_2D(s, xstates, ystates, actions)
    p = init_probs(x_size, y_size)
    p = update_all_P(p, all_K)

    sc = init_k(x_size, y_size)
    all_Kc = det_all_k_2D(sc, xstates, ystates, new_actions)
    pc = init_probs(x_size, y_size)
    pc = update_all_P(pc, all_Kc)
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
    if pc[target] > .80 and not lock_80c:
        lock_80c = True
        table['ts_80c'].append(time_steps)
        table['er_80c'].append(errors)
    elif pc[target] > .90 and not lock_90c:
        lock_90c = True
        table['ts_90c'].append(time_steps)
        table['er_90c'].append(errors)
    elif pc[target] > .95 and not lock_95c:
        lock_95c = True
        table['ts_95c'].append(time_steps)
        table['er_95c'].append(errors)      
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
        if not lock_80c:
            table['ts_80c'].append(None)
            table['er_80c'].append(None)
        else:
            lock_80c = False
        if not lock_90c:
            table['ts_90c'].append(None)
            table['er_90c'].append(None)
        else:
            lock_90c = False        
        if not lock_95c:
            table['ts_95c'].append(None)
            table['er_95c'].append(None)   
        else:
            lock_95c = False
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
    subs2 = rospy.Subscriber('classification', Int32, clf_callback)
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
    lock_80c = False
    lock_90c = False
    lock_95c = False
    table = {'ts_80': [], 'ts_90': [], 'ts_95': [],'er_80': [], 'er_90': [], 'er_95': [],\
     'ts_80c': [], 'ts_90c': [], 'ts_95c': [],'er_80c': [], 'er_90c': [], 'er_95c': [], 'er': []}
    rospy.init_node('subs', anonymous=True)
    err = rospy.get_param('~err')
    err = \
    {(0,0):0.6,(0,1):0.1,(0,2):0.1,(0,3):0.1,(0,4):0.1,\
    (1,0):0.1,(1,1):0.6,(1,2):0.1,(1,3):0.1,(1,4):0.1,\
    (2,0):0.1,(2,1):0.1,(2,2):0.6,(2,3):0.1,(2,4):0.1,\
    (3,0):0.1,(3,1):0.1,(3,2):0.1,(3,3):0.6,(3,4):0.1,\
    (4,0):0.1,(4,1):0.1,(4,2):0.1,(4,3):0.1,(4,4):0.6}
    beta_param = rospy.get_param('~bp')
    denoiser = Denoiser(err, beta_param, [0,1,2,3,4])
    target = (3, 3)
    x_size = 10
    y_size = 10
    log = []
    target_log = []
    time_steps = 0
    main()