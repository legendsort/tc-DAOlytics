#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_network.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
from os.path import exists
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from compute_network import compute_network
from plot_network import plot_network_num_interactions
from compute_metrics import compute_metrics
from plot_network_metrics import plot_network_metrics

# # # # # set parameter values # # # # #

FILENAME = "./data/community_analytics.csv" # name of file with discord data (add path if stored in different directory)

DIR = True # whether directed or undirected networks should be created for plotting the network
SHOW = [True, True] # whether plotted figures should be shown
REMOVE_ACCOUNTS = ["MEE6#4876", "sesh#1244", 'Dework#9886'] # list of account names that should not be considered in the analysis
# TODO MERGE_ACCOUNTS = [] # list of tuples with account names that should be merged
SEL_RANGE = [0,np.inf]#1657885015236] # range of time indices to include in analysis (inclusive)

EMOJI_TYPES = None # emoji's to be considered. (set to None for all emojis)   # thank you: ["❤", "💜", "💜", "🙏", "❤️", "🙌"]   voting: ["🤙", "👍"]
MEN_SUBSTRING = None # mentions in messages containing substrings specified in this list are considered only (set to None for all messages)
REACT_SUBSTRING = None # emoji reactions to messages containing substrings specified in this list are considered only (set to None for all messages)
REPLY_SUBSTRING = None # replies containing substrings specified in this list are considered only (set to None for all messages)

INTERACTION_WEIGHTS = [1,1,1,1] # relative weight of mentions, reactions, replies and threads

NODE_MULT = 5 # node multiplication for plotting
EDGE_MULT = 0.2 # edge multiplication for plotting
NODE_LEG_VALS = [10, 50, 100] # values to plot for node legend
EDGE_LEG_VALS = [1, 10, 30] # values to plot for edge legend
NODE_POS_SCALE = 15 # location scale multiplication for plotting


# # # # # main function # # # # # 

def main(args):
    
    # # # DEFINE FILE IDENTIFIER # # #
    
    # parse discord data file name
	split1 = FILENAME.split("/")
	split2 = split1[-1].split(".")
    
    # make file identifier
	file_identifier = "{}_dir{}_selRange{}{}_weights{}{}{}{}".format(\
		split2[0], DIR, SEL_RANGE[0], SEL_RANGE[1], INTERACTION_WEIGHTS[0], \
		INTERACTION_WEIGHTS[1], INTERACTION_WEIGHTS[2], INTERACTION_WEIGHTS[3])
    
    		
	# # # COMPUTE NETWORK # # #
	
	total_graph, men_graph, react_graph, reply_graph, thread_graph, acc_names = \
		compute_network(FILENAME, DIR, REMOVE_ACCOUNTS, SEL_RANGE, EMOJI_TYPES, \
		MEN_SUBSTRING, REACT_SUBSTRING, REPLY_SUBSTRING, INTERACTION_WEIGHTS)		
	
	
	# # # MAKE FIGURE OF NETWORK # # #
	
	# make save path for network figure (set to None for figure not to be saved)
	net_fig_save_path = "./results/figures/network_fig_"+file_identifier+".png"
		
	# create network figure
	plot_network_num_interactions(total_graph, men_graph, react_graph, reply_graph, \
		thread_graph, acc_names, DIR, SHOW[0], NODE_MULT, EDGE_MULT, NODE_LEG_VALS, \
		EDGE_LEG_VALS, NODE_POS_SCALE, net_fig_save_path)
	
	
	# # # COMPUTE NETWORK METRICS # # #
	
	[node_clus, node_sp, node_betw, sw, edge_dist] = compute_metrics(total_graph[0])
	
	
	
	# # # MAKE FIGURE OF NETWORK METRICS # # #
	
	# make save path for network metrics figure (set to None for figure not to be saved)
	net_met_fig_save_path = "./results/figures/network_metrics_fig_"+file_identifier+".png"
	
	# create network metrics figure
	net_metrics_fig = plot_network_metrics(node_clus, node_sp, node_betw, \
		sw, edge_dist, total_graph[1], total_graph[2], SHOW[1], net_met_fig_save_path)
	

if __name__ == '__main__':
	sys.exit(main(sys.argv))
