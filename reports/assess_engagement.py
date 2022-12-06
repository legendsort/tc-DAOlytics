#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_network.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 
 
# # # # # import libraries # # # # #

import sys
import os
import csv
import numpy as np
import networkx as nx
import copy as copy
from datetime import datetime
from collections import Counter


# # # # # main function # # # # #

def assess_engagement(graph, w_i, acc_names, INT_TYPE, INT_THR, UW_DEG_THR, \
	EDGE_STR_THR, UW_THR_DEG_THR, CON_T_THR, CON_O_THR, VITAL_T_THR, \
	VITAL_O_THR, PAUSED_T_THR, STILL_T_THR, STILL_O_THR, WINDOW_D, \
	n_arrived, n_consistent, n_vital, n_non_vital, n_active, n_connected, \
	n_periphery, n_paused, n_new_disengaged, n_disengaged, n_unpaused, \
	n_returned, n_new_active, n_still_active, all_arrived, all_consistent, \
	all_vital, all_non_vital, all_active, all_connected, all_periphery, \
	all_paused, all_new_disengaged, all_disengaged, all_unpaused, \
	all_returned, all_new_active, all_still_active):
	"""
	Assess engagment levels for all active members in a time period
	
	Input:
	graph - (graph, 1D np.array, 1D np.array) : (the graph object,
		weighted degree, fraction of weighted in degree)
	w_i - int : index of sliding time window
	acc_names - [str] : all active accounts in window
	INT_TYPE - str : indicates what interaction type should be 
		considered (either "in", "out" or "all")
	INT_THR - int : minimum number of interactions to be active
	UW_DEG_THR - int : minimum number of connections to be active	
	EDGE_STR_THR - int : minimum number of interactions for connected
	UW_THR_DEG_THR - int : minimum number of accounts for connected
	CON_T_THR - int : time period to assess consistently active
	CON_O_THR - int : times to be active within CON_T_THR to be 
		consistently active
	VITAL_T_THR - int : time period to assess for vital
	VITAL_O_THR - int : times to be connected within VITAL_T_THR to be vital
	PAUSED_T_THR - int : time period to remain paused	
	STILL_T_THR - int : time period to assess for still active
	STILL_O_THR - int : times to be active within STILL_T_THR to be still active
	WINDOW_D - int : duration of sliding window (days)
	STEP_D - int : step size of sliding window (days)
	n_* - [int] : list of number of accounts in engagement category * 
		for all previous windows
	all_* - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names belonging to engagement
		category *

	Output:
	n_* - [int] : list of number of accounts in engagement category * 
		updated for window w_i
	all_* - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names belonging to engagement
		category * updated for window w_i
	"""
	
	# # # SEPARATE IN AND OUT INTERACTIONS # # #
		
	# select number of interactions per account based on INT_TYPE
	int_analysis = sep_in_out(graph, INT_TYPE)
		
			
	# # # THRESHOLD INTERACTIONS # # #
		
	thr_ind, thr_uw_deg, thr_uw_thr_deg = thr_int(graph, int_analysis, \
		INT_THR, UW_DEG_THR, EDGE_STR_THR, UW_THR_DEG_THR)
		

	# # # ACTIVE # # #
	
	n_active, all_active = assess_active(acc_names, thr_ind, thr_uw_deg, \
		w_i, n_active, all_active)
		
		
	# # # # CONNECTED # # #
		
	n_connected, all_connected = assess_connected(acc_names, thr_uw_thr_deg, \
		w_i, n_connected, all_connected)
		
		
	# # # PERIPHERY # # #
	
	n_periphery, all_periphery = assess_periphery(all_active, all_connected, \
		w_i, n_periphery, all_periphery)
		
			
	# # # CONSISTENTLY ACTIVE # # #
		
	n_consistent, all_consistent = assess_consistent(all_active, w_i, \
		CON_T_THR, CON_O_THR, WINDOW_D, n_consistent, all_consistent)
				
		
	# # # VITAL # # #
	
	n_vital, all_vital = assess_vital(all_connected, w_i, VITAL_T_THR, \
		VITAL_O_THR, WINDOW_D, n_vital, all_vital)
			
		
	# # # NON VITAL # # #
	
	n_non_vital, all_non_vital = assess_non_vital(all_active, all_vital, w_i, \
		n_non_vital, all_non_vital)
		
		
	# # # STILL ACTIVE # # #
	
	n_still_active, all_still_active = assess_still_active(all_arrived, \
		all_active, w_i, STILL_T_THR, STILL_O_THR, WINDOW_D, n_still_active, \
		all_still_active)		
			
						
	# # # REMAINDER # # # 
	
	n_new_active, all_new_active, n_unpaused, all_unpaused, n_returned, \
		all_returned, n_paused, all_paused, n_new_disengaged, all_new_disengaged, \
		n_disengaged, all_disengaged = assess_remainder(all_active, w_i, WINDOW_D, \
		PAUSED_T_THR, n_new_active, all_new_active, n_unpaused, all_unpaused, n_returned, \
		all_returned, n_paused, all_paused, n_new_disengaged, all_new_disengaged, \
		n_disengaged, all_disengaged)	

		
	return [n_arrived, n_consistent, n_vital, n_non_vital, n_active, n_connected, \
		n_periphery, n_paused, n_new_disengaged, n_disengaged, n_unpaused, \
		n_returned, n_new_active, n_still_active, all_arrived, all_consistent, all_vital, \
		all_non_vital, all_active, all_connected, all_periphery, all_paused, \
		all_new_disengaged, all_disengaged, all_unpaused, all_returned, \
		all_new_active, all_still_active]


# # # # # nested functions # # # # #

def sep_in_out(graph, INT_TYPE):
	"""
	Selects the number of interactions per account based on INT_TYPE
	
	Input:
	graph - (graph, 1D np.array, 1D np.array) : (the graph object,
		weighted degree, fraction of weighted in degree)
	INT_TYPE - str : indicates what interaction type should be 
		considered (either "in", "out" or "all")
		
	Output:
	int_analysis - [int] : number of INT_TYPE interactions per account
	"""
			
	# compute number of ingoing interactions
	int_in = ((graph[2]+1)/2) * graph[1] 
		
	# compute number of outgoing interactions
	int_out = graph[1] - int_in
		
	if INT_TYPE == "in":
		int_analysis = int_in
	elif INT_TYPE == "out":
		int_analysis = int_out
	elif INT_TYPE == "all":
		int_analysis = graph[1]
	else:
		print("ERROR: Set INT_TYPE to 'in', 'out' or 'all'")
		return None
	
	return int_analysis
		
# # #

def thr_int(graph, int_analysis, INT_THR, UW_DEG_THR, EDGE_STR_THR, UW_THR_DEG_THR):
	"""
	Computes number of interactions and connections per account
	
	Input:
	graph - (graph, 1D np.array, 1D np.array) : (the graph object,
		weighted degree, fraction of weighted in degree)
	int_analysis - [int] : number of INT_TYPE interactions per account
	INT_THR - int : minimum number of interactions to be active	
	UW_DEG_THR - int : minimum number of connections to be active
	EDGE_STR_THR - int : minimum number of interactions for connected
	UW_THR_DEG_THR - int : minimum number of accounts for connected
		
	Output:
	thr_ind - [int] : index numbers of account names with at least
		INT_THR interactions
	thr_uw_deg - [int] : index numbers of account names with at least
		UW_DEG_THR connections
	thr_uw_thr_deg - [int] : index numbers of account names with at
		least UW_THR_DEG_THR connections of at least EDGE_STR_THR
		interactions each
	"""
				
	# # # TOTAL INTERACTIONS # # #
	
	# compare total weighted node degree to interaction threshold
	thr_ind = np.where(int_analysis >= INT_THR)[0]
	
		
	# # # TOTAL CONNECTIONS # # #
	
	# get unweighted node degree value for each node
	all_degrees = np.array([val for (node, val) in graph[0].degree()])
		
	# compare total unweighted node degree to interaction threshold
	thr_uw_deg = np.where(all_degrees >= UW_DEG_THR)[0]
		
	
	# # # THRESHOLDED CONNECTIONS # # #
		
	# make copy of graph for thresholding
	thresh_graph = copy.deepcopy(graph[0])
		
	# remove edges below threshold from copy
	thresh_graph.remove_edges_from([(n1, n2) for n1, n2, w in thresh_graph.edges(data="weight") if w < EDGE_STR_THR])
		
	# get unweighted node degree value for each node from thresholded network
	all_degrees_thresh = np.array([val for (node, val) in thresh_graph.degree()])
		
	# compare total unweighted node degree after thresholding to threshold
	thr_uw_thr_deg = np.where(all_degrees_thresh > UW_THR_DEG_THR)[0]
	
	
	return [thr_ind, thr_uw_deg, thr_uw_thr_deg]
	
# # #

def assess_active(acc_names, thr_ind, thr_uw_deg, w_i, n_active, all_active):
	"""
	Assess all active accounts

	Input:
	acc_names - [str] : all active accounts in window
	thr_ind - [int] : index numbers of account names with at least
		INT_THR interactions
	thr_uw_deg - [int] : index numbers of account names with at least
		UW_DEG_THR connections
	w_i - int : index of sliding time window
	n_active - [int] : list of number of accounts that are active
	all_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are active	

	Output:
	n_active - [int] : list of number of accounts that are active 
		updated for window w_i
	all_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are active updated 
		for window w_i	
	"""
		
	# # obtain accounts that meet both weigthed and unweighted degree thresholds
	thr_overlap = np.intersect1d(thr_ind, thr_uw_deg)
		
	# store number of accounts above threshold
	n_active[w_i] = len(thr_overlap)
		
	# obtain active account names in this period and store in dictionary
	all_active[str(w_i)] = acc_names[thr_overlap]
	
	return [n_active, all_active]
	
# # #

def assess_connected(acc_names, thr_uw_thr_deg, w_i, n_connected, all_connected):
	"""
	Assess all connected accounts

	Input:
	acc_names - [str] : all active accounts in window
	thr_uw_thr_deg - [int] : index numbers of account names with at
		least UW_THR_DEG_THR connections of at least EDGE_STR_THR
		interactions each
	w_i - int : index of sliding time window
	n_connected - [int] : list of number of accounts that are connected
	all_connected - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are connected	

	Output:
	n_connected - [int] : list of number of accounts that are connected 
		updated for window w_i
	all_connected - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are connected updated 
		for window w_i	
	"""
	
	# store number of accounts above thresholded unweighted degree threshold
	n_connected[w_i] = len(thr_uw_thr_deg)
		
	# obtain connected account names in this period and store in dictionary
	all_connected[str(w_i)] = acc_names[thr_uw_thr_deg]
	
	return [n_connected, all_connected]
	
# # #	

def assess_periphery(all_active, all_connected, w_i, n_periphery, all_periphery):
	"""
	Assess all periphery accounts

	Input:
	all_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are active
	all_connected - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are connected	
	w_i - int : index of sliding time window
	n_periphery - [int] : list of number of accounts that are periphery
	all_periphery - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are periphery	
			
	Output:
	n_periphery - [int] : list of number of accounts that are periphery 
		updated for window w_i
	all_periphery - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are periphery updated 
		for window w_i	
	"""
	
	# store number remaining account names in periphery
	all_periphery[str(w_i)] = set(all_active[str(w_i)])-set(all_connected[str(w_i)])
				
	# store number remaining account names in periphery
	n_periphery[w_i] = len(all_periphery[str(w_i)])
	
	return [n_periphery, all_periphery]
	
# # #

def assess_consistent(all_active, w_i, CON_T_THR, CON_O_THR, WINDOW_D, \
	n_consistent, all_consistent):
	"""
	Assess all continuously active accounts

	Input:
	all_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are active
	w_i - int : index of sliding time window
	CON_T_THR - int : time period to assess consistently active
	CON_O_THR - int : times to be active within CON_T_THR to be 
		consistently active
	WINDOW_D - int : duration of sliding window (days)	
	n_consistent - [int] : list of number of accounts that are continuously active
	all_consistent - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are continuously active	

	Output:
	n_consistent - [int] : list of number of accounts that are consistently active 
		updated for window w_i
	all_consistent - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are consistently active updated 
		for window w_i
	"""
	
	# if there are more time periods in the past than CON_T_THR
	if w_i-(CON_T_THR-1)*WINDOW_D >= 0:
		
		# obtain who was consistently active in all specified time periods
		all_consistent[str(w_i)] = check_past(all_active, CON_T_THR, CON_O_THR, WINDOW_D)
		
	else:
			
		# store empty set 
		all_consistent[str(w_i)] = set("")
			
	# store number of continuously active members
	n_consistent[w_i] = len(all_consistent[str(w_i)])
			
	return [n_consistent, all_consistent]
	
# # #

def assess_vital(all_connected, w_i, VITAL_T_THR, VITAL_O_THR, WINDOW_D, n_vital, all_vital):
	"""
	Assess all vital accounts

	Input:
	all_connected - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are connected	
	w_i - int : index of sliding time window
	VITAL_T_THR - int : time period to assess for vital
	VITAL_O_THR - int : times to be connected within VITAL_T_THR to be vital
	WINDOW_D - int : duration of sliding window (days)
	n_vital - [int] : list of number of accounts that are vital
	all_vital - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are vital	
		
	Output:
	n_vital - [int] : list of number of accounts that are vital 
		updated for window w_i
	all_vital - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are vital updated 
		for window w_i
	"""
		
	# if there are more time periods in the past than CON_T_THR
	if w_i-VITAL_T_THR*WINDOW_D >= 0:
				
		# obtain who was connected in all specified time periods and was engaged
		all_vital[str(w_i)] = set(check_past(all_connected, VITAL_T_THR, VITAL_O_THR, WINDOW_D))
		
	else:
			
		# store empty set 
		all_vital[str(w_i)] = set("")
						
	# store number of vital members
	n_vital[w_i] = len(all_vital[str(w_i)])
	
	return [n_vital, all_vital]
	
# # #

def assess_non_vital(all_active, all_vital, w_i, n_non_vital, all_non_vital):
	"""
	Assess all non-vital accounts

	Input:
	all_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are active	
	all_vital - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are vital
	w_i - int : index of sliding time window
	n_non_vital - [int] : list of number of accounts that are non vital
	all_non_vital - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are non vital	
			
	Output:
	n_non_vital - [int] : list of number of accounts that are non vital 
		updated for window w_i
	all_non_vital - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are non vital updated 
		for window w_i
	"""
	
	# store remaining account names in non vital
	all_non_vital[str(w_i)] = set(all_active[str(w_i)])-set(all_vital[str(w_i)])
		
	# store number remaining account names in non vital
	n_non_vital[w_i] = len(all_non_vital[str(w_i)])
	
	return [n_non_vital, all_non_vital]
	
# # #

def assess_still_active(all_arrived, all_active, w_i, STILL_T_THR, \
	STILL_O_THR, WINDOW_D, n_still_active, all_still_active):
	"""
	Assess all still active accounts

	Input:
	all_arrived - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that arrived in period	
	all_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are active	
	w_i - int : index of sliding time window
	STILL_T_THR - int : time period to assess for still active
	STILL_O_THR - int : times to be active within STILL_T_THR to be still active
	WINDOW_D - int : duration of sliding window (days)
	n_still_active - [int] : list of number of accounts that are still active
	all_still_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are still active
			
	Output:
	n_still_active - [int] : list of number of accounts that are still 
		active updated for window w_i
	all_still_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are still active
		updated for window w_i
		
	"""
	
	# if there are more time periods in the past than STILL_T_THR
	if w_i-(STILL_T_THR)*WINDOW_D >= 0:
				
		# obtain who was active in sufficient specified time periods 
		all_con_active = set(check_past(all_active, STILL_T_THR, STILL_O_THR, WINDOW_D))
		
		# select who of all_con_active were part of all arrived in period and store
		all_still_active[str(w_i)] = all_con_active.intersection(all_arrived[str(w_i-(STILL_T_THR)*WINDOW_D)])
		
	else:
			
		# store empty set 
		all_still_active[str(w_i)] = set("")
						
	# store number of vital members
	n_still_active[w_i] = len(all_still_active[str(w_i)])
	
	return [n_still_active, all_still_active]
	
# # #

def assess_remainder(all_active, w_i, WINDOW_D, PAUSED_T_THR, n_new_active, all_new_active, \
	n_unpaused, all_unpaused, n_returned, all_returned, n_paused, all_paused, \
	n_new_disengaged, all_new_disengaged, n_disengaged, all_disengaged):
	"""
	Assess all remaing engagement categories

	Input:
	all_active - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are active	
	w_i - int : index of sliding time window
	WINDOW_D - int : duration of sliding window (days)
	PAUSED_T_THR - int : time period to remain paused	
	n_* - [int] : list of number of accounts that are *
	all_* - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are *	
			
	Output:
	n_* - [int] : list of number of accounts that are * 
		updated for window w_i
	all_* - {str : [str]} : dictionary with keys w_i and values
		containing a list of all account names that are * updated 
		for window w_i
	"""
					
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
		
	return [n_new_active, all_new_active, n_unpaused, all_unpaused, n_returned, \
		all_returned, n_paused, all_paused, n_new_disengaged, all_new_disengaged, \
		n_disengaged, all_disengaged]
		
# # #	

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
	
