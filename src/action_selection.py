import operator
import random

def init_probs(x_size, y_size):
    P = {}
    for i in range(0, x_size):
        for j in range(0, y_size):
            P[(i, j)] = 0
    num_states = len(P)
    for key in P:
        P[key] = 1./num_states
    return P

def init_k(x_size, y_size):
    k = {}
    for i in range(0, x_size):
        for j in range(0, y_size):
            k[(i, j)] = []
    return k

def det_k(P,prev_state,action, response):
    kl = 1
    kh = 2
    
    if action == 'east' and response == 1:
        for key in P:
            if key[0] <= prev_state[0]:
                P[key] = kl
            if key[0] > prev_state[0]:
                P[key] = kh
    elif action == 'west' and response == 1:
        for key in P:
            if key[0] < prev_state[0]:
                P[key] = kh
            if key[0] >= prev_state[0]:
                P[key] = kl
    elif action == 'north' and response == 1:
        for key in P:
            if key[1] < prev_state[1]:
                P[key] = kh
            if key[1] >= prev_state[0]:
                P[key] = kl
    elif action == 'south' and response == 1:
        for key in P:
            if key[1] <= prev_state[1]:
                P[key] = kl
            if key[1] < prev_state[1]:
                P[key] = kh

    elif action == 'east' and response == 0:
        for key in P:
            if key[0] <= prev_state[0]:
                P[key] = kh
            if key[0] > prev_state[0]:
                P[key] = kl
    elif action == 'west' and response == 0:
        for key in P:
            if key[0] < prev_state[0]:
                P[key] = kl
            if key[0] >= prev_state[0]:
                P[key] = kh
    elif action == 'north' and response == 0:
        for key in P:
            if key[1] < prev_state[1]:
                P[key] = kl
            if key[1] >= prev_state[0]:
                P[key] = kh
    elif action == 'south' and response == 0:
        for key in P:
            if key[1] <= prev_state[1]:
                P[key] = kh
            if key[1] < prev_state[1]:
                P[key] = kl
    return P

def det_all_k(s,states,actions):
    kl = 1
    kh = 1.5
    ka = (kl+kh)/2.
    P = s

    for i in range(len(states)):
        if actions[i] == 0:
            for key in P:
                if key[0] < states[i]:
                    P[key].append(kh)
                elif key[0] >= states[i]:
                    P[key].append(kl)
        elif actions[i] == 2:
            for key in P:
                if key[0] > states[i]:
                    P[key].append(kh)
                elif key[0] <= states[i]:
                    P[key].append(kl)
        elif actions[i] == 1:
            for key in P:
                if key[0] == states[i]:
                    P[key].append(kh)
                else:
                    P[key].append(kl)
    return P

def update_P(P,K):
    norm = 0
    for key in P:
        norm += P[key]*K[key]
    for key in P:
        P[key] = K[key]*P[key]/float(norm)
    return P

def update_all_P(P,K):
    #print K
    for i in range(len(K[(0,0)])):
        norm = 0
        for key in P:
            norm += P[key]*K[key][i]
        for key in P:
            P[key] = K[key][i]*P[key]/float(norm)
    return P

def get_max(P):
    maximum =  max(P.iteritems(), key=operator.itemgetter(1))[1]
    maxim = []
    for key in P:
        if P[key] == maximum:
            maxim.append(key)
    return maxim

def get_max_state(P):
    maximum =  max(P.iteritems(), key=operator.itemgetter(1))[1]
    maxim = []
    for key in P:
        if P[key] == maximum:
            maxim.append(key)
    return maxim[0]

def get_min(P):
    minimum =  min(P.iteritems(), key=operator.itemgetter(1))[1]
    min_s = []
    for key in P:
        if P[key] == minimum:
            min_s.append(key)
    return min_s[0]

def get_min_actions(actions):
    minimum =  min(actions.iteritems(), key=operator.itemgetter(1))[1]
    min_a = []
    for key in actions:
        if actions[key] == minimum:
            min_a.append(key)
    return min_a

def manhattan_dist(state_a,state_b):
    return abs(state_a[0] - state_b[0]) + abs(state_a[1] - state_b[1])

def get_target(current_state,S_max):
    state_dict = {}
    for state in S_max:
        if current_state != state:
            state_dict[state] = manhattan_dist(current_state, state)

    try:
        target = get_min(state_dict)
    except ValueError:
        target = current_state
    return target

def move(s, a, x_size, y_size): 
    if a == 'east' and s[0] != x_size - 1:
        return (s[0]+1,s[1])
    if a == 'north' and s[1] != 0:
        return (s[0],s[1]-1)
    if a == 'west' and s[0] != 0:
        return (s[0]-1,s[1])
    if a == 'south' and s[1] != y_size - 1:
        return (s[0],s[1]+1)
    else:
        return s
        
def get_s_h_l(current_s, action, S_max, x_size, y_size):   
    s_h = {}
    #print S_max
    s_h[(current_s,action)] = []
    s_l = {}
    s_l[(current_s,action)] = []
    for state in S_max:
        if manhattan_dist(move(current_s,action, x_size, y_size),state) <= manhattan_dist(current_s,state):
            s_h[(current_s,action)].append(state)
        if manhattan_dist(move(current_s,action, x_size, y_size),state) > manhattan_dist(current_s,state):
            s_l[(current_s,action)].append(state)
    return(s_h,s_l)

def get_delta_action(current_s, S_max, actions, x_size, y_size):
    delta_action_dict = {}
    for action in actions:
        (s_h,s_l) = get_s_h_l(current_s, action, S_max, x_size, y_size)
        s_h_num = len(s_h[(current_s,action)])
        s_l_num = len(s_l[(current_s,action)])
        delta_action = abs(s_h_num - s_l_num)
        delta_action_dict[action] = delta_action
    #print delta_action_dict
    return delta_action_dict
    
def pick_action(current_state, actions, P, x_size, y_size, ts):
    #print P
    S_max = get_max(P)

    target_state = get_target(current_state, S_max)
    delta_action_dict = get_delta_action(current_state, S_max, actions, x_size, y_size)
    actions = get_min_actions(delta_action_dict)
    selection = 0
    if len(actions) == 1:
        return actions[0]
    elif len(actions) > 1:
        for action in actions:
            if manhattan_dist(move(current_state,action, x_size, y_size),target_state) < manhattan_dist(current_state,target_state):
                selection = action          
    if len(actions) == 0:
        return 'stay'
    if selection == 0:
        #selection = random.choice(actions)
        if ts > 16:
            neighbors = {}
            if current_state[1] != y_size - 1:
                neighbors[(current_state[0],current_state[1]+1)] = P[(current_state[0],current_state[1]+1)]
            if current_state[1] != 0:
                neighbors[(current_state[0],current_state[1]-1)] = P[(current_state[0],current_state[1]-1)]
            if current_state[0] != x_size - 1:
                neighbors[(current_state[0]+1,current_state[1])] = P[(current_state[0]+1,current_state[1])]
            if current_state[0] != 0:
                neighbors[(current_state[0]-1,current_state[1])] = P[(current_state[0]-1,current_state[1])]
            state = get_max_state(neighbors)

            if state[0] > current_state[0]:
                selection = 'east'
            elif state[1] > current_state[1]:
                selection = 'south'
            elif state[0] < current_state[0]:
                selection = 'west'
            elif state[1] < current_state[1]:
                selection = 'north'
        else:
            selection = random.choice(actions)
        #print selection
    else:
        return selection
    return selection

if __name__=="__main__":
    x_size = 4
    y_size = 4
    P = init_probs(x_size, y_size)
    K = det_k(P,(0,3),'east')
    P = update_P(P,K)
    S = get_max(P)
    T = get_target((2,0),S)
    action = pick_action((0, 3), ['east','west','north','south'], P, x_size, y_size)
    print T
    print action