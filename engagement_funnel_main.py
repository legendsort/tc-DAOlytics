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
from collections import Counter

from load_data import load_csv_data
from compute_network import compute_network
from assess_arrivals import assess_arrivals
import plot_engagement_data 


# # # # # set parameter values # # # # #

DATA_DIR_PATH = "./data/aragon220919/" # path to directory with discord data
ARR_CHANNELS = None #["arrivals"] # path to directory/direcotires with arrival data
CHANNELS = ["ambassadorchat", "anttoken", "bugsfeedback", "communitygeneral", \
	"communitywellbeing", "daoexpertsgenerl", "daopolls", "data", \
	"design", "devspace", "dgov", "espanol", \
	"finance", "general", "governancegeneral", "growthsquad", \
	"kudos", "learninglibrary", "legal", "meetups", \
	"memespets", "newjoiners", "operationsgeneral", \
	"questions", "spamreporting", "support", \
	"tweetsnews"] # names of channels to be used for analysis (should correspond to directories in DATA_DIR_PATH)
TEMP_THREAD_DIR_PATH = "./temp_thread" # path to temporary directory where thread data from all channels will be combined

DIR = True # whether directed or undirected networks should be created for plotting the network
SHOW = [True, True] # whether plotted figures should be shown
REMOVE_ACCOUNTS = ["Aragon🦅 Blog#0000", "Aragon🦅 Twitter#0000"] # list of account names that should not be considered in the analysis
MERGE_ACCOUNTS = [] # list of tuples with account names that should be merged (only first name in tuple remains)
SEL_RANGE = ['22/04/01 00:00:00', '22/09/18 00:00:00'] # range of dates and times to include in analysis ('yy/mm/dd HH:MM:SS')
WINDOW_D = 7
STEP_D = 1

INT_THR = 1 # minimum number of interactions to be active					Default = 
UW_DEG_THR = 1 # minimum number of accounts interacted with to be active	Default = 
PAUSED_T_THR = 2 # time period to remain paused								Default = 
CONT_T_THR = 2 # time period to be continously active						Default = 
EDGE_STR_THR = 5 # minimum number of interactions for connected				Default = 
UW_THR_DEG_THR = 5 # minimum number of accounts for connected				Default = 
CORE_T_THR = 5 # time period to assess for core								Default = 
CORE_O_THR = 3 # times to be connected within CORE_T_THR to be core			Default =

PLOT_MEM_TYPE = "" #""  # "core"  # "discovering"  # "engaged" 
INT_TYPE = "all" # "in"  "out"  "all"
RAND = False

PER_TABLE = 4;
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]

EMOJI_TYPES = None # emoji's to be considered. (set to None for all emojis)   # thank you: ["❤", "💜", "💜", "🙏", "❤️", "🙌"]   voting: ["🤙", "👍"]
MEN_SUBSTRING = None # mentions in messages containing substrings specified in this list are considered only (set to None for all messages)
REACT_SUBSTRING = None # emoji reactions to messages containing substrings specified in this list are considered only (set to None for all messages)
REPLY_SUBSTRING = None # replies containing substrings specified in this list are considered only (set to None for all messages)

INTERACTION_WEIGHTS = [1,1,1,1] # relative weight of mentions, reactions, replies and threads

N_BINS = 10

NODE_CLUS_MAX = 1
NODE_SP_MAX = 4
NODE_BETW_MAX = 0.1
EDGE_W_MAX = 60
NODE_D_MAX = 20

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
					
		# compute network	
		total_graph, men_graph, react_graph, reply_graph, thread_graph, acc_names = \
			compute_network(data, DIR, REMOVE_ACCOUNTS, MERGE_ACCOUNTS, \
			t_sel_range_str, EMOJI_TYPES, MEN_SUBSTRING, REACT_SUBSTRING, REPLY_SUBSTRING, \
			INTERACTION_WEIGHTS, TEMP_THREAD_DIR_PATH)	
			
		
		# # # SEPARATE IN AND OUT INTERACTIONS # # #
				
		# compute number of ingoing interactions
		int_in = ((total_graph[2]+1)/2) * total_graph[1] 
		
		# compute number of outgoing interactions
		int_out = total_graph[1] - int_in
		
		if INT_TYPE == "in":
			int_analysis = int_in
		elif INT_TYPE == "out":
			int_analysis = int_out
		elif INT_TYPE == "all":
			int_analysis = total_graph[1]
		else:
			print("ERROR: Set INT_TYPE to 'in', 'out' or 'all'")
			return
			
		
		# # # THRESHOLD INTERACTIONS # # #
					
		# # weighted degree
		
		# compare total weighted node degree to interaction threshold
		thr_ind = np.where(int_analysis > INT_THR)[0]
		
		# # unweighted degree
		
		# get unweighted node degree value for each node
		all_degrees = np.array([val for (node, val) in total_graph[0].degree()])
		
		# compare total unweighted node degree to interaction threshold
		thr_uw_deg = np.where(all_degrees > UW_DEG_THR)[0]
		
		# # thresholded unweighted degree
		
		# make copy of graph for thresholding
		thresh_graph = total_graph[0]
		
		# remove edges below threshold from copy
		thresh_graph.remove_edges_from([(n1, n2) for n1, n2, w in thresh_graph.edges(data="weight") if w < EDGE_STR_THR])
		
		# get unweighted node degree value for each node from thresholded network
		all_degrees_thresh = np.array([val for (node, val) in thresh_graph.degree()])
		
		# compare total unweighted node degree after thresholding to threshold
		thr_uw_thr_deg = np.where(all_degrees_thresh > UW_THR_DEG_THR)[0]
		
		
		# # # ACTIVE # # #
		
		# # obtain accounts that meet both weigthed and unweighted degree thresholds
		thr_overlap = np.intersect1d(thr_ind, thr_uw_deg)
		
		# store number of accounts above threshold
		n_active[w_i] = len(thr_overlap)
		
		# obtain active account names in this period and store in dictionary
		all_active[str(w_i)] = acc_names[thr_overlap]
		
		
		# # # CONNECTED # # #
		
		# # store number of accounts above thresholded unweighted degree threshold
		n_connected[w_i] = len(thr_uw_thr_deg)
		
		# obtain connected account names in this period and store in dictionary
		all_connected[str(w_i)] = acc_names[thr_uw_thr_deg]
		
		
		# # # PERIPHERY # # #
		
		# store number remaining account names in periphery
		all_periphery[str(w_i)] = set(all_active[str(w_i)])-set(all_connected[str(w_i)])
				
		# store number remaining account names in periphery
		n_periphery[w_i] = len(all_periphery[str(w_i)])
		
			
		# # # CONTINUOUSLY ACTIVE # # #
		
		# if there are more time periods in the past than CONT_T_THR
		if w_i-(CONT_T_THR-1)*WINDOW_D >= 0:
		
			# obtain who was continously active in all specified time periods
			all_continous[str(w_i)] = check_past(all_active, CONT_T_THR, CONT_T_THR, WINDOW_D)
		
		else:
			
			# store empty set 
			all_continous[str(w_i)] = set("")
			
		# store nubmer of engaged members
		n_continous[w_i] = len(all_continous[str(w_i)])
			
		
		
		# # # CORE # # #
		
		# if there are more time periods in the past than CONT_T_THR
		if w_i-CORE_T_THR*WINDOW_D >= 0:
				
			# obtain who was connected in all specified time periods and was engaged
			all_core[str(w_i)] = set(check_past(all_connected, CORE_T_THR, CORE_O_THR, WINDOW_D))
		
		else:
			
			# store empty set 
			all_core[str(w_i)] = set("")
						
		# store number of core members
		n_core[w_i] = len(all_core[str(w_i)])
			
		
		# # # NON CORE # # #
		
		# store remaining account names in non core
		all_non_core[str(w_i)] = set(all_active[str(w_i)])-set(all_core[str(w_i)])
		
		# store number remaining account names in non core
		n_non_core[w_i] = len(all_non_core[str(w_i)])
			
						
		# # ASSESS ENGAGEMENT LEVEL # # # 		
					
		# if data from previous period is available
		if w_i-WINDOW_D >= 0:
			
			# check if there is paused data from previous period and otherwise make empty set
			temp_set_paused = check_prev_period(all_paused, str(w_i-WINDOW_D))
			
			# check if there is disengaged data from previous period and otherwise make empty set
			temp_set_disengaged = check_prev_period(all_disengaged, str(w_i-WINDOW_D))
			
			# check if there is unpaused data from previous period and otherwise make empty set
			temp_set_unpaused = check_prev_period(all_unpaused, str(w_i-WINDOW_D))

				
			# # # NEWLY ACTIVE # # #
			
			# obtain members active in this window that were not active, paused or disengaged WINDOW_D days ago
			all_new_active[str(w_i)] = set(all_active[str(w_i)])-set(all_active[str(w_i-WINDOW_D)]) - temp_set_paused - temp_set_disengaged - temp_set_unpaused
			
			# store number of new joiners
			n_new_active[w_i] = len(all_new_active[str(w_i)])
			
			
			# # # PAUSED (1 of 2)# # #
			
			# obtain members that were active WINDOW_D days ago but are not active in this window
			new_paused = set(all_active[str(w_i-WINDOW_D)])-set(all_active[str(w_i)])			
			
			# add newly paused members to paused members from previous period
			temp_currently_paused = new_paused.union(temp_set_paused)
			
			# create temporary empty set result (will be updated in part 2 of 2)
			all_paused[str(w_i)] = set("")
			
											
			# if data from previous previous period is available
			if w_i-2*WINDOW_D >= 0:
				
				
				# # # UNPAUSED # # #
								
				# obtain account names active now but paused WINDOW_D days ago
				all_unpaused[str(w_i)] = set(all_paused[str(w_i-WINDOW_D)]).intersection(all_active[str(w_i)])
				
				# store number of unpaused
				n_unpaused[w_i] = len(all_unpaused[str(w_i)])
				
				# remove unpaused from currently paused
				temp_currently_paused = temp_currently_paused - all_unpaused[str(w_i)]
				
				
				# # # RETURNED # # #
				
				# if there is disengaged data for this time period
				if str(w_i-WINDOW_D) in all_disengaged.keys():

					# obtain account names active now but disengaged WINDOW_D days ago	
					all_returned[str(w_i)] = set(all_disengaged[str(w_i-WINDOW_D)]).intersection(all_active[str(w_i)])
					
				else:
					
					# store empty set for returned
					all_returned[str(w_i)] = set("")
					
				# count number of returned accounts
				n_returned[w_i] = len(all_returned[str(w_i)])
						
					
				# # # DISENGAGED # # #
				
				# obtain account names that were continuously paused for PAUSED_T_THR periods
				cont_paused = check_past(all_paused, PAUSED_T_THR+1, PAUSED_T_THR, WINDOW_D)
				
				# obtain account names that were continuously paused and are still not active
				all_new_disengaged[str(w_i)] = cont_paused.intersection(temp_currently_paused)
				
				# add newly disengaged members to disengaged members from previous period
				temp_currently_disengaged = all_new_disengaged[str(w_i)].union(temp_set_disengaged) 

				# remove returned accounts from disengaged accounts and store
				all_disengaged[str(w_i)] = temp_currently_disengaged - all_returned[str(w_i)]
				
				# store number of disengagers
				n_disengaged[w_i] = len(all_disengaged[str(w_i)])
				n_new_disengaged[w_i] = len(all_new_disengaged[str(w_i)])
				
				# remove disengaged accounts from paused accounts
				temp_currently_paused = temp_currently_paused - all_disengaged[str(w_i)]
				
			
			# # # PAUSED (2 of 2) # # #
			
			# store currently paused accounts
			all_paused[str(w_i)] = temp_currently_paused
			
			# store number of paused accounts
			n_paused[w_i] = len(all_paused[str(w_i)])
			
		else:
			
			# set all active members to newly active
			all_new_active[str(w_i)] = set(all_active[str(w_i)])
			
			# store number of new joiners
			n_new_active[w_i] = len(all_new_active[str(w_i)])	
							
									
	# # # SAVE RESULTS # # # 
	
	# save results as pkl files for internal loading
	with open('./engagement_funnel_data.pkl', 'wb') as f:
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
	ac_mem_save_path = "./results/figures/Aragon_engagement_active_members_rand{}".format(int(RAND)) # exclude .png in name
	
	# plot results
	plot_engagement_data.plot_active_members(all_active, all_connected, \
		all_periphery, all_core, all_non_core, all_new_active, all_unpaused, \
		all_returned, all_continous, date_tick_i, date_tick_labels, \
		PER_TABLE, WINDOW_D, RAND, SHOW[0], ac_mem_save_path) 


	# # # PLOT RESULTS FOR INACTIVATING MEMBERS # # #
	
	# make save path for active member figure (set to None for figure not to be saved)
	inac_mem_save_path = "./results/figures/Aragon_engagement_inactivating_members_rand{}".format(int(RAND)) # exclude .png in name
	
	# plot results
	plot_engagement_data.plot_inactive_members(all_active, all_connected, \
		all_paused, all_core, all_new_disengaged, all_new_active, all_unpaused, \
		all_returned, all_continous, PAUSED_T_THR, date_tick_i, date_tick_labels, \
		PER_TABLE, WINDOW_D, RAND, SHOW[1], inac_mem_save_path) 	


# # # OTHER FUNCTIONS # # #

def check_prev_period(engagement_dict, time_str):
	"""
	Checks if values are present in specific previous period of dict
	
	Input:
	engagement_dict - {str : set} : dictionary with account names sets  
		as values for periods indicated as keys
	time_str - str : dictionary key of interest
	
	Output:
	temp_set - set : either the set that is the value for the time_str 
		key or and empty set		
	"""
			
	# if engagement_dict contains data for time_str
	if time_str in engagement_dict.keys():
		temp_set = set(engagement_dict[time_str]) 
	else:
		temp_set = set("")
			
	return temp_set
	
				
# # #

def check_past(data_dic, t_thr, o_thr, WINDOW_D):
	"""
	Checks in how many previous periods account names were in a dict
	
	Input:
	data_dic - {str : set} : dictionary with account name sets to check
	t_thr - int : number of time period into the past to consider
	o_thr - int : minimal number of occurences of account name within 
		the period specified by t_thr
	WINDOW_D - int : width of an analysis window in number of days
	
	Output:
	acc_selection - [str] : all accounts that were present in data_dic
		for more than o_thr times within the last t_thr periods
	"""
	
	# initiate empty result list
	acc_per_period = [None]*t_thr
			
	# obtain dictionary keys
	dic_keys = list(data_dic.keys())
		
	# for each period that should be considered
	for p in range(t_thr):
		
		# if time period is present in dic_keys
		if len(dic_keys) >= -(-1-(p*WINDOW_D)):
								
			# obtain accounts in period
			acc_per_period[p] = list(data_dic[str(dic_keys[-1-(p*WINDOW_D)])])
			
		else:
			
			# store empty values
			acc_per_period[p] = list("")
	
	# merge values in list of list into single list
	all_acc_list = [elem for sublist in acc_per_period for elem in sublist]
	
	# count number of occurences in list per account
	acc_cnt_dict = Counter(all_acc_list)
	
	# obtain account names that with at least o_thr occurences in all_acc_list
	acc_selection = set([acc for acc, occurrences in acc_cnt_dict.items() if occurrences >= o_thr])

	return acc_selection
	


if __name__ == '__main__':
	sys.exit(main(sys.argv))
