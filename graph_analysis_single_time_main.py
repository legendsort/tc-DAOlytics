#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_network.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import os
import shutil
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from load_data import load_csv_data
from compute_network import compute_network
from plot_network import plot_network_num_interactions
from compute_metrics import compute_metrics
from plot_network_metrics import plot_network_metrics

# # # # # set parameter values # # # # #

DATA_DIR_PATH = "./data/aragon220919/" # path to directory with discord data
CHANNELS = ["ambassadorchat", "anttoken", "bugsfeedback", "communitygeneral", "communitywellbeing", "daoexpertsgenerl", "daopolls", "data", \
	"design", "devspace", "dgov", "espanol", \
	"finance", "general", "governancegeneral", "growthsquad", \
	"kudos", "learninglibrary", "legal", "meetups", \
	"memespets", "newjoiners", "operationsgeneral", \
	"questions", "spamreporting", "support", \
	"tweetsnews"] # names of channels to be used for analysis (should correspond to directories in DATA_DIR_PATH)

# CHANNELS = ["biz_dev", "community_health", "compensation", "cooperative_unit", \
	# "credentials", "dao_blocks_framework", "dao_speaks", "energy", \
	# "fun_and_off_topic", "general_chat", "general_dao_work", "gratitude_n_praise", \
	# "learning_n_discussion", "level1", "multisig", "pre_proposals", \
	# "proposals", "public_announcements", "research_coordination", \
	# "research_repository", "rewards_compensation", "share_the_love", \
	# "show_n_tell"] # names of channels to be used for analysis (should correspond to directories in DATA_DIR_PATH)

TEMP_THREAD_DIR_PATH = "./temp_thread" # path to temporary directory where thread data from all channels will be combined

DIR = True # whether directed or undirected networks should be created for plotting the network
SHOW = [True, True] # whether plotted figures should be shown
FIG_TYPE = "clusters" # whether network nodes should be colored based on in-out fraction ("in-out") or clustering ("clusters")
REMOVE_ACCOUNTS = ["Aragon🦅 Blog#0000", "Aragon🦅 Twitter#0000"] #["MEE6#4876", "sesh#1244", "Dework#9886", "RnDAO Bot#0000", "RnPulse#2107"] # list of account names that should not be considered in the analysis
MERGE_ACCOUNTS = []#[("thegadget.eth#3374", "sepehr#3795"), ("Shanzz#5133", "Shanzz 🏴#5133")] # list of tuples with account names that should be merged (only first name in tuple remains)
SEL_RANGE = ['22/09/12 00:00:00', '22/09/18 00:00:00'] #['22/04/17 00:00:00', '22/08/17 00:00:00'] # range of dates and times to include in analysis ('yy/mm/dd HH:MM:SS')

EMOJI_TYPES = None # emoji's to be considered. (set to None for all emojis)   # thank you: ["❤", "💜", "💜", "🙏", "❤️", "🙌"]   voting: ["🤙", "👍"]
MEN_SUBSTRING = None # mentions in messages containing substrings specified in this list are considered only (set to None for all messages)
REACT_SUBSTRING = None # emoji reactions to messages containing substrings specified in this list are considered only (set to None for all messages)
REPLY_SUBSTRING = None # replies containing substrings specified in this list are considered only (set to None for all messages)

INTERACTION_WEIGHTS = [1,1,1,1] # relative weight of mentions, reactions, replies and threads

NODE_MULT = 15 # node multiplication for plotting
EDGE_MULT = 1 # edge multiplication for plotting
NODE_LEG_VALS = [5, 100, 500] # values to plot for node legend
EDGE_LEG_VALS = [1, 10, 50] # values to plot for edge legend
NODE_POS_SCALE = 0.1 # location scale multiplication for plotting


# # # # # main function # # # # # 

def main(args):
    
    # # # DEFINE FILE IDENTIFIER # # #
		
	# make file identifier based on parameter selection
	file_identifier = "aragon_analysis_220912_220918_dir{}_weights{}{}{}{}".format(\
		DIR, INTERACTION_WEIGHTS[0], INTERACTION_WEIGHTS[1], INTERACTION_WEIGHTS[2],\
		INTERACTION_WEIGHTS[3])
			
		    
	# # # LOAD AND CONCATENATE DATA # # #
	
	# remove temporary directory for thread data if it exists
	if os.path.exists(TEMP_THREAD_DIR_PATH):
		shutil.rmtree(TEMP_THREAD_DIR_PATH)
		
	# make temporary directory for all thread data
	os.mkdir(TEMP_THREAD_DIR_PATH)
		
	# load all data from specified channels into one data file
	data = load_csv_data(CHANNELS, DATA_DIR_PATH, TEMP_THREAD_DIR_PATH)
	
				
	# # # COMPUTE NETWORK # # #
	
	total_graph, men_graph, react_graph, reply_graph, thread_graph, acc_names = \
		compute_network(data, DIR, REMOVE_ACCOUNTS, MERGE_ACCOUNTS, \
		SEL_RANGE, EMOJI_TYPES, MEN_SUBSTRING, REACT_SUBSTRING, REPLY_SUBSTRING, \
		INTERACTION_WEIGHTS, TEMP_THREAD_DIR_PATH)		
				

	# # # MAKE FIGURE OF NETWORK # # #
	
	# make save path for network figure (set to None for figure not to be saved)
	net_fig_save_path = None #"./results/figures/network_fig_"+file_identifier+".png"
		
	# create network figure
	plot_network_num_interactions(total_graph, men_graph, react_graph, reply_graph, \
		thread_graph, acc_names, DIR, SHOW[0], NODE_MULT, EDGE_MULT, NODE_LEG_VALS, \
		EDGE_LEG_VALS, NODE_POS_SCALE, FIG_TYPE, net_fig_save_path)
	
	print("Receivers: {}".format(np.sum(total_graph[2] > 0.5)))
	print("Instigators: {}".format(np.sum(total_graph[2] < -0.5)))
	
	# # # COMPUTE NETWORK METRICS # # #
	
	[node_clus, node_sp, node_betw, sw, edge_dist, lc_nodes] = compute_metrics(total_graph[0])
	
	print("There are {} active accounts in total".format(len(lc_nodes)))
	
	
	# # # MAKE FIGURE OF NETWORK METRICS # # #
	
	# make save path for network metrics figure (set to None for figure not to be saved)
	net_met_fig_save_path = None #"./results/figures/network_metrics_fig_"+file_identifier+".png"
	
	# create network metrics figure
	net_metrics_fig = plot_network_metrics(node_clus, node_sp, node_betw, \
		sw, edge_dist, total_graph[1][list(lc_nodes)], total_graph[2][list(lc_nodes)], \
		SHOW[1], net_met_fig_save_path)
	
	
	# # # REMOVE TEMPORARY DIRECTORY WITH THREAD DATA # # #
	shutil.rmtree(TEMP_THREAD_DIR_PATH)

if __name__ == '__main__':
	sys.exit(main(sys.argv))
