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
import csv
import pickle
from matplotlib.lines import Line2D
from datetime import datetime
from dateutil.relativedelta import relativedelta

from load_data import load_csv_data
from assess_arrivals import assess_arrivals
from compute_network import compute_network
import assess_engagement
import plot_engagement_data 
from plot_network import plot_network_num_interactions
from compute_metrics import compute_metrics
from plot_network_metrics import plot_network_metrics



# # # # # set parameter values # # # # #

COMMUNITY_ID = "aragon220919" # folder name for loading and saving data
# COMMUNITY_ID = "test" # folder name for loading and saving data
DATA_DIR_PATH = "./data/{}/".format(COMMUNITY_ID) # path to directory with discord data
ARR_CHANNELS = None #["arrivals"] # path to directory/direcotires with arrival data
CHANNELS = ["ambassadorchat", "anttoken", "bugsfeedback", "communitygeneral", \
	"communitywellbeing", "daoexpertsgenerl", "daopolls", "data", \
	"design", "devspace", "dgov", "espanol", \
	"finance", "general", "governancegeneral", "growthsquad", \
	"kudos", "learninglibrary", "legal", "meetups", \
	"memespets", "newjoiners", "operationsgeneral", \
	"questions", "spamreporting", "support", \
	"tweetsnews"] # names of channels to be used for analysis (should correspond to directories in DATA_DIR_PATH)
# CHANNELS = ["general_full"]
TEMP_THREAD_DIR_PATH = "./temp_thread" # path to temporary directory where thread data from all channels will be combined

DIR = True # whether directed or undirected networks should be created for plotting the network
SHOW = [True, True, True, True, True] # whether plotted figures should be shown
REMOVE_ACCOUNTS = ["Aragon🦅 Blog#0000", "Aragon🦅 Twitter#0000"] # list of account names that should not be considered in the analysis
MERGE_ACCOUNTS = [] # list of tuples with account names that should be merged (only first name in tuple remains)
SEL_RANGE = ['22/08/01 00:00:00', '22/09/18 00:00:00'] # range of dates and times to include in analysis ('yy/mm/dd HH:MM:SS')
WINDOW_D = 7 # duration of sliding window (days)
STEP_D = 1 # step size of sliding window (days)

INT_THR = 1 # minimum number of interactions to be active					Default = 1
UW_DEG_THR = 1 # minimum number of accounts interacted with to be active	Default = 1
PAUSED_T_THR = 2 # time period to remain paused								Default = 2
CONT_T_THR = 2 # time period to be continously active						Default = 2
EDGE_STR_THR = 5 # minimum number of interactions for connected				Default = 5
UW_THR_DEG_THR = 5 # minimum number of accounts for connected				Default = 5
CORE_T_THR = 5 # time period to assess for core								Default = 5
CORE_O_THR = 3 # times to be connected within CORE_T_THR to be core			Default = 3

INT_TYPE = "all" # "in"  "out"  "all"
RAND = False

PER_TABLE = 4;
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]

EMOJI_TYPES = None # emoji's to be considered. (set to None for all emojis)   # thank you: ["❤", "💜", "💜", "🙏", "❤️", "🙌"]   voting: ["🤙", "👍"]
MEN_SUBSTRING = None # mentions in messages containing substrings specified in this list are considered only (set to None for all messages)
REACT_SUBSTRING = None # emoji reactions to messages containing substrings specified in this list are considered only (set to None for all messages)
REPLY_SUBSTRING = None # replies containing substrings specified in this list are considered only (set to None for all messages)

INTERACTION_WEIGHTS = [1,1,1,1] # relative weight of mentions, reactions, replies and threads

FIG_TYPE = "in-out" # whether network nodes should be colored based on in-out fraction ("in-out") or clustering ("clusters")
NODE_MULT = 15 # node multiplication for plotting
EDGE_MULT = 1 # edge multiplication for plotting
NODE_LEG_VALS = [5, 100, 500] # values to plot for node legend
EDGE_LEG_VALS = [1, 10, 50] # values to plot for edge legend
NODE_POS_SCALE = 0.1 # location scale multiplication for plotting

# # # # # main function # # # # # 

def main(args):
    
    # # load saved data
	# with open('./engagement_funnel_data.pkl', 'rb') as f:
		# pickle_out = pickle.load(f)
	
	# n_arrived = pickle_out[0]
	# n_continous = pickle_out[1]
	# n_core = pickle_out[2]
	# n_non_core = pickle_out[3]
	# n_active = pickle_out[4]
	# n_connected = pickle_out[5]
	# n_periphery = pickle_out[6]
	# n_paused = pickle_out[7]
	# n_new_disengaged = pickle_out[8]
	# n_disengaged = pickle_out[9]
	# n_unpaused = pickle_out[10]
	# n_returned = pickle_out[11]
	# n_new_active = pickle_out[12]
	# all_arrived = pickle_out[13]
	# all_continous = pickle_out[14]
	# all_core = pickle_out[15]
	# all_non_core = pickle_out[16]
	# all_active = pickle_out[17]
	# all_connected = pickle_out[18]
	# all_periphery = pickle_out[19]
	# all_paused = pickle_out[20]
	# all_new_disengaged = pickle_out[21]
	# all_disengaged = pickle_out[22]
	# all_unpaused = pickle_out[23]
	# all_returned = pickle_out[24]
	# all_new_active = pickle_out[25]
	# date_tick_i = pickle_out[26]
	# date_tick_labels = pickle_out[27]	
	
    # # # LOAD AND CONCATENATE DATA # # #
    
    # remove temporary directory for thread data if it exists
	if os.path.exists(TEMP_THREAD_DIR_PATH):
		shutil.rmtree(TEMP_THREAD_DIR_PATH)
    
    # make temporary directory for all thread data
	os.mkdir(TEMP_THREAD_DIR_PATH)
    
    # load all data from specified channels into one data file
	data = load_csv_data(CHANNELS, DATA_DIR_PATH, TEMP_THREAD_DIR_PATH)
		
	# load arrival data
	if ARR_CHANNELS != None:
		arr_data = load_csv_data(ARR_CHANNELS, DATA_DIR_PATH, TEMP_THREAD_DIR_PATH)
		
    		
	# # # DEFINE SLIDING WINDOW RANGE # # #
	
	# determine window start times
	start_dt = datetime.strptime(SEL_RANGE[0], '%y/%m/%d %H:%M:%S')
	end_dt = datetime.strptime(SEL_RANGE[1], '%y/%m/%d %H:%M:%S')
	
	time_diff = end_dt - start_dt
	
	# determine maximum start time
	last_start = time_diff - relativedelta(days=WINDOW_D)
	
	
	# # # RESULT ARRAYS # # #
	
	# initiate empty result arrays		
	n_arrived = np.zeros(last_start.days+1)
	n_continous = np.zeros(last_start.days+1)
	n_core = np.zeros(last_start.days+1)
	n_non_core = np.zeros(last_start.days+1)
	
	n_active = np.zeros(last_start.days+1)
	n_connected = np.zeros(last_start.days+1)
	n_periphery = np.zeros(last_start.days+1)
	n_paused = np.zeros(last_start.days+1)
	n_new_disengaged = np.zeros(last_start.days+1)
	n_disengaged = np.zeros(last_start.days+1)
	n_unpaused = np.zeros(last_start.days+1)
	n_returned = np.zeros(last_start.days+1)
	n_new_active = np.zeros(last_start.days+1)
	
	net_decen = np.zeros(last_start.days+1)
	sw = np.zeros(last_start.days+1)
	node_clus_av = np.zeros(last_start.days+1)
	node_sp_av = np.zeros(last_start.days+1)
	node_betw_av = np.zeros(last_start.days+1)
	num_edge = np.zeros(last_start.days+1)
	num_node = np.zeros(last_start.days+1)
	edge_dens = np.zeros(last_start.days+1)
		
	
	# initiate empty result libraries
	all_arrived = {}
	all_continous = {}
	all_core = {}
	all_non_core = {}
	
	all_active = {}
	all_connected = {}
	all_periphery = {}
	all_new_active = {}
	all_paused = {}
	all_new_disengaged = {}
	all_disengaged = {}
	all_unpaused = {}
	all_returned = {}
	
	node_clus = {}
	node_sp = {}
	node_betw = {}
	edge_weights = {}
	lc_nodes = {}
	
	
	# initiate empty result arrays for tick labels
	date_tick_i = []
	date_tick_labels = []
	
	
	# # # ACTUAL ANALYSIS # # # 
		
	# for every window index
	for w_i in range(int(np.floor(last_start.days/STEP_D)+1)):
		
		print("window {} of {}".format(w_i+1, int(np.floor(last_start.days/STEP_D)+1)))	
		
		# # # DEFINE RANGE SINGLE WINDOW # # #
			
		# set temporary selection range
		t_sel_range = np.asarray([start_dt + relativedelta(days=STEP_D*w_i), \
			start_dt + relativedelta(days=STEP_D*w_i) + relativedelta(days=WINDOW_D)])
				
		# make empty array for datetime string values
		t_sel_range_str = np.zeros_like(t_sel_range)
		
		# turn date time values into string 
		for i in range(len(t_sel_range)):
			t_sel_range_str[i] = t_sel_range[i].strftime('%y/%m/%d %H:%M:%S')
			
		
		# # # DATE TICK LABELS # # #
		
		# if the window starts at the first day of the month
		if t_sel_range[0].day == 1:
			
			# store window index
			date_tick_i.append(w_i)
			
			# store date tick label
			date_tick_labels.append(MONTH_NAMES[t_sel_range[0].month-1] + " 1st")
			
		
		# # # ARRIVALS # # #
					
		# obtain new arrivals in time period
		if ARR_CHANNELS != None:
			n_arrived[w_i], all_arrived[str(w_i)] = assess_arrivals(arr_data, t_sel_range_str)
		
		
		# # # NETWORK # # #
	
		# compute network for this time window
		total_graph, men_graph, react_graph, reply_graph, thread_graph, acc_names = \
			compute_network(data, DIR, REMOVE_ACCOUNTS, MERGE_ACCOUNTS, \
			t_sel_range_str, EMOJI_TYPES, MEN_SUBSTRING, REACT_SUBSTRING, REPLY_SUBSTRING, \
			INTERACTION_WEIGHTS, TEMP_THREAD_DIR_PATH)	
			
				
		# # # ENGAGEMENT # # #
		
		# compute engagement levels for this time window
		[n_arrived, n_continous, n_core, n_non_core, n_active, n_connected, \
			n_periphery, n_paused, n_new_disengaged, n_disengaged, n_unpaused, \
			n_returned, n_new_active, all_arrived, all_continous, all_core, \
			all_non_core, all_active, all_connected, all_periphery, all_paused, \
			all_new_disengaged, all_disengaged, all_unpaused, all_returned, \
			all_new_active] = assess_engagement.assess_engagement(total_graph, w_i, \
			acc_names, INT_TYPE, INT_THR, UW_DEG_THR, EDGE_STR_THR, UW_THR_DEG_THR, \
			CONT_T_THR, CORE_T_THR, CORE_O_THR, PAUSED_T_THR, WINDOW_D,\
			n_arrived, n_continous, n_core, n_non_core, n_active, n_connected, \
			n_periphery, n_paused, n_new_disengaged, n_disengaged, n_unpaused, \
			n_returned, n_new_active, all_arrived, all_continous, all_core, \
			all_non_core, all_active, all_connected, all_periphery, all_paused, \
			all_new_disengaged, all_disengaged, all_unpaused, all_returned, \
			all_new_active)
		
		
		# # # NETWORK METRICS # # #
		
		# # compute network metrics for this time window
		# [node_clus[str(w_i)], node_sp[str(w_i)], node_betw[str(w_i)], \
			# net_decen[w_i], sw[w_i], edge_weights[str(w_i)], lc_nodes[str(w_i)]] = \
			# compute_metrics(total_graph[0])
		
		# # compute number of edges and nodes for this time window and store
		# num_edge[w_i] = len(edge_weights[str(w_i)])
		# num_node[w_i] = len(lc_nodes[str(w_i)])		
		# edge_dens[w_i] = 100 * (num_edge[w_i] / (0.5 * num_node[w_i] * (num_node[w_i] - 1)))	
	
		# # store average node metrics for engagement subtypes
		# [node_clus_av, node_sp_av, node_betw_av] = store_av_metrics_engagement_subset(\
			# all_core, acc_names, lc_nodes, w_i, node_clus, node_sp, node_betw, \
			# node_clus_av, node_sp_av, node_betw_av)
		
		# # store average node metrics for engagement subtypes
		# [node_clus_av, node_sp_av, node_betw_av] = store_av_metrics_engagement_subset(\
			# all_non_core, acc_names, lc_nodes, w_i, node_clus, node_sp, node_betw, \
			# node_clus_av, node_sp_av, node_betw_av)
			

	# # SAVE RESULTS # # # 
	
	# save results as pkl files for internal loading
	with open('./engagement_funnel_data_new.pkl', 'wb') as f:
		pickle.dump([n_arrived, n_continous, n_core, n_non_core, n_active, \
		n_connected, n_periphery, n_paused, n_new_disengaged, n_disengaged, n_unpaused, n_returned, \
		n_new_active, all_arrived, all_continous, all_core, all_non_core, \
		all_active, all_connected, all_periphery, all_paused, all_new_disengaged, \
		all_disengaged, all_unpaused, all_returned, all_new_active, date_tick_i, date_tick_labels], f)
			
	print(".pkl variables saved")
			
	# save results in csv format for external plotting
	np.savetxt("aragon_activity_levels_time_series.csv", (n_arrived, \
		n_continous, n_core, n_non_core, n_active, n_connected, n_periphery, \
		n_paused, n_new_disengaged, n_disengaged, n_unpaused, n_returned, \
		n_new_active), fmt="%.0f", delimiter=',', \
		header="arrived,continuous,core,non-core,active,connected,periphery,paused,new disengaged,disengaged,unpaused,returned,new active") 
	
	# save date indicators in csv format for external plotting
	np.savetxt("aragaon_activity_date_indicators.csv", (date_tick_i, date_tick_labels), \
		fmt="%s", delimiter=',', header="list indices,date labels")
	
	print(".csv variables saved")
	
			
	# # # PLOT RESULTS FOR ACTIVE MEMBERS # # #
	
	# make save path for active member figure (set to None for figure not to be saved)
	ac_mem_save_path = None #"./results/figures/Aragon_engagement_active_members_rand{}".format(int(RAND)) # exclude .png in name
	
	# plot results
	plot_engagement_data.plot_active_members(all_active, all_connected, \
		all_periphery, all_core, all_non_core, all_new_active, all_unpaused, \
		all_returned, all_continous, date_tick_i, date_tick_labels, \
		PER_TABLE, WINDOW_D, RAND, SHOW[0], ac_mem_save_path) 


	# # # PLOT RESULTS FOR INACTIVATING MEMBERS # # #
	
	# make save path for active member figure (set to None for figure not to be saved)
	inac_mem_save_path = None #"./results/figures/Aragon_engagement_inactivating_members_rand{}".format(int(RAND)) # exclude .png in name
	
	# plot results
	plot_engagement_data.plot_inactive_members(all_active, all_connected, \
		all_paused, all_core, all_new_disengaged, all_new_active, all_unpaused, \
		all_returned, all_continous, PAUSED_T_THR, date_tick_i, date_tick_labels, \
		PER_TABLE, WINDOW_D, RAND, SHOW[1], inac_mem_save_path) 	
		
		
	# # # PLOT RATIO OF UNPAUSING MEMBERS # # #
	
	# make save path for active member figure (set to None for figure not to be saved)
	unp_mem_save_path = None #"./results/figures/Aragon_engagement_unpaused_member_ratio_cut.png"
	
	plot_engagement_data.plot_unpaused_score(n_unpaused, n_new_disengaged, \
		date_tick_i, date_tick_labels, SHOW[2], unp_mem_save_path)


	# # # PLOT FIGURE OF NETWORK # # #
	
	# make save path for network figure (set to None for figure not to be saved)
	net_fig_save_path = None #"./results/figures/Aragon_network_fig.png"
			
	# create network figure
	plot_network_num_interactions(total_graph, men_graph, react_graph, reply_graph, \
		thread_graph, acc_names, DIR, SHOW[3], NODE_MULT, EDGE_MULT, NODE_LEG_VALS, \
		EDGE_LEG_VALS, NODE_POS_SCALE, FIG_TYPE, net_fig_save_path)
	
		
	# # # MAKE FIGURE OF NETWORK METRICS # # #
	
	# make save path for network metrics figure (set to None for figure not to be saved)
	net_met_fig_save_path = None #"./results/figures/Aragon_network_metrics_fig.png"
	
	# create network metrics figure
	net_metrics_fig = plot_network_metrics(node_clus, node_sp, node_betw, \
		sw, edge_dist, total_graph[1][list(lc_nodes)], total_graph[2][list(lc_nodes)], \
		SHOW[4], net_met_fig_save_path)	
		
		
		
# # # # # OTHER FUNCTIONS # # # # #

def store_av_metrics_engagement_subset(comparison, acc_names, lc_nodes, w_i, node_clus, node_sp, \
	node_betw, node_clus_av, node_sp_av, node_betw_av):
		
	# obtain all account names of lc_nodes
	lc_acc_names = acc_names[list(lc_nodes[str(w_i)])]
	
	# obtain account names in comparison and in lc
	overlap_i = [i for i, val in enumerate(lc_acc_names) if val in comparison[str(w_i)]]
	
	# compute average of metrics and store
	node_clus_av[w_i] = np.average(node_clus[str(w_i)][overlap_i])
	node_sp_av[w_i] = np.average(node_sp[str(w_i)][overlap_i])
	node_betw_av[w_i] = np.average(node_betw[str(w_i)][overlap_i])

	

	return [node_clus_av, node_sp_av, node_betw_av]
	
	
if __name__ == '__main__':
	sys.exit(main(sys.argv))
