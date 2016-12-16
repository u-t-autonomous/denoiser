from math import log
import maxflow
import sys
from itertools import combinations
from random import choice
from math import log
from random import shuffle
import itertools

class Denoiser:
    
    def __init__(self, param, beta_param, labels):
        self.param = param
        self.beta_param = beta_param
        self.labels = labels

    def D(self, evaluation, label):
        if evaluation == label:
            return -log(1 - self.param)
        else:
            return -log(self.param)

    def V(self, evaluation, label):
        if evaluation == label:
            return 0
        else:
            return self.beta_param

    def E(self, original_eval, new_eval):
        d_cost = sum(map(self.D,original_eval, new_eval))
        v_cost = sum(map(self.V,new_eval[0:-1],new_eval[1:]))
        energy = d_cost + v_cost
        return energy

    def neighbors_map(self, evals, alpha, beta):
        neighbors = {}
        for i, ev in enumerate(evals):
            if i == 0 and len(evals) != 1:
                if evals[i+1] not in [alpha, beta]:
                    neighbors[i] = [evals[i+1]]
                else:
                    neighbors[i] = []
            elif i == len(evals)-1:
                if evals[i-1] not in [alpha, beta]:
                    neighbors[i] = [evals[i-1]]
                else:
                    neighbors[i] = []
            else:
                evs = [evals[i-1],evals[i+1]]
                neighbors[i] = [x for x in evs if x not in [alpha, beta]]
        return neighbors


    def make_graph_swap(self, new_evals, original_eval, alpha, beta):
        n_link = self.V(alpha, beta)
        indices = []
        g = maxflow.Graph[float](200, 200)
        neighbors = self.neighbors_map(new_evals, alpha, beta)
        for i, ev in enumerate(new_evals):         
            if ev in [alpha, beta]:
                if len(neighbors[i]) != 0:
                    t_alpha = self.D(original_eval[i], alpha) + sum(map(self.V, neighbors[i], [alpha]*len(neighbors[i])))
                    t_beta = self.D(original_eval[i], beta) + sum(map(self.V, neighbors[i], [beta]*len(neighbors[i])))
                else:
                    t_alpha = self.D(original_eval[i], alpha) + 0
                    t_beta = self.D(original_eval[i], beta) + 0            
                indices.append(i)
                node = g.add_nodes(1)
                g.add_tedge(node[0], t_alpha, t_beta)
                if i != 0:
                    if new_evals[i-1] in [alpha, beta]:
                        g.add_edge(node[0], node[0]-1, n_link, n_link)
        return g, indices

    def make_graph_expand(self, new_evals, original_eval, alpha):
        indices = []
        g = maxflow.Graph[float](200, 200)
        node_next = False
        for i, ev in enumerate(new_evals):
            t_alpha = self.D(original_eval[i], alpha) #+ 1     # adding this term ( + 1) makes a difference      
            if node_next == False:
                node = g.add_nodes(1)
                
            else:
                node = node_next
                node_next = False    
                
            indices.append(node[0])
            
            if ev == alpha:
                t_not_alpha = 100000000
            else:
                t_not_alpha = self.D(new_evals[i], original_eval[i])
                
            g.add_tedge(node[0], t_alpha, t_not_alpha)
 
            if i != len(new_evals) - 1:           
                if ev != new_evals[i+1]:
                    node_a = g.add_nodes(1)
                    node_next = g.add_nodes(1)
                    t_a_not_alpha = self.V(ev, new_evals[i+1])
                    g.add_tedge(node_a[0], 0, t_a_not_alpha)
                    e_p_a = self.V(ev, alpha)
                    g.add_edge(node[0], node_a[0], e_p_a, e_p_a)
                    e_a_q = self.V(new_evals[i+1], alpha)
                    g.add_edge(node_next[0], node_a[0], e_a_q, e_a_q)
                else:
                    node_next = g.add_nodes(1)
                    e_p_q = self.V(ev, alpha)
                    g.add_edge(node_next[0], node[0], e_p_q, e_p_q)
                    
        return g, indices

    def construct_evals_swap(self, f, graph, indices, alpha, beta):
        for i, index in enumerate(indices):
            if graph.get_segment(i) == 1:
                f[index] = alpha
            else:
                f[index] = beta
        return f

    def construct_evals_expand(self, f, graph, indices, label):
        for i, index in enumerate(indices):
            if graph.get_segment(index) == 1:
                f[i] = label
        return f    
    
    def swap(self, evals, pairs = None):
        f = evals
        e_value = self.E(evals, evals)
        if pairs == None:
            pairs = list(combinations(self.labels, 2))
        success = True
        while success:
            success = False
            for pair in pairs:
                graph, indices = self.make_graph_swap(f, evals, pair[0], pair[1])
                graph.maxflow()
                new_evals = self.construct_evals_swap(f,graph, indices, pair[0], pair[1])
                new_e_value = self.E(evals, new_evals)
                if new_e_value < e_value:
                    f = new_evals
                    e_value = new_e_value
                    success = True
        return f

    def expand(self, evals):
        f = evals
        e_value = self.E(evals, evals)
        success = True
        while success:
            success = False
            for label in self.labels:
                graph, indices = self.make_graph_expand(f, evals, label)
#                 plot_graph_3d(graph, (10,10,10))
                graph.maxflow()
                new_evals = self.construct_evals_expand(f,graph, indices, label)
                new_e_value = self.E(evals, new_evals)
                if new_e_value < e_value:
                    f = new_evals
                    e_value = new_e_value
                    success = True
        return f