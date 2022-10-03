#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_network_metrics.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import random


def plot_active_members(all_active, all_connected, all_periphery, all_core, \
	all_non_core, all_new_active, all_unpaused, all_returned, all_continous, \
	date_tick_i, date_tick_labels, PER_TABLE, WINDOW_D, RAND, SHOW, SAVE_PATH=None):
	"""
	Plots active member graphs from engagement data
	
	Input:
	all_* - {str: set} : dictionary with all * account names for each
		analysis period
	date_tick_i - [int] : dictionary key values that correspond to dates
		that should be plotted as tick labels for the plots
	date_tick_labels - [str] : dates corresponding to the date_tick_i indices
	PER_TABLE - int : number of periods shown in the table
	WINDOW_D - int : width of an analysis window in number of days
	RAND - bool : whether values should be randomized before plotting
	SHOW - bool : whether figure should be shown
	SAVE_PATH = str : path to where figure should be saved, existing figures
		 with same path are overwritten. Set to None to not save figure (default = None)
		 
	Output:
	act_mem_fig - fig : figure object with recent activity data
	act_mem_hist_fig - fig : figure object with history of activity data
	Plots and/or saves figure based on SHOW and SAVE_PATH values
	"""
	
	# terminate function if output should not be saved or shown
	if SAVE_PATH == None and not SHOW:
		return
		
	# # # GENERAL PREPARATIONS # # #
	
	# set activity type colors
	act_type_colors = ['#a6cee3', '#1f78b4',  '#b2df8a', '#33a02c']  # for: new, unpaused, returend, continous respectively

	
	# obtain overlap between activity type and engagement level
	[continous_all, new_active_all, unpaused_all, returned_all], _ = \
		assess_overlap(all_active, [all_continous, all_new_active, all_unpaused, \
		all_returned], len(all_active.keys()), 0, True, RAND)
	
	[continous_conn, new_active_conn, unpaused_conn, returned_conn], _ = \
		assess_overlap(all_connected, [all_continous, all_new_active, all_unpaused, \
		all_returned], len(all_active.keys()), 0, True, RAND)
	
	[continous_per, new_active_per, unpaused_per, returned_per], _ = \
		assess_overlap(all_periphery, [all_continous, all_new_active, all_unpaused, \
		all_returned], len(all_active.keys()), 0, True, RAND)
		
	[continous_core, new_active_core, unpaused_core, returned_core], _ = \
		assess_overlap(all_core, [all_continous, all_new_active, all_unpaused, \
		all_returned], len(all_active.keys()), 0, True, RAND)
	
	[continous_ncore, new_active_ncore, unpaused_ncore, returned_ncore], _ = \
		assess_overlap(all_non_core, [all_continous, all_new_active, all_unpaused, \
		all_returned], len(all_active.keys()), 0, True, RAND)
		
	# initiate first figure
	act_mem_fig = plt.figure(figsize=(8,3))
	
	
	# # # CURRENT PERIOD BARPLOT # # #
			
	# initiate subplot for current period
	curr_ax = act_mem_fig.add_subplot(1,2,1)
	
	# specify what to plot
	mem_type_labels = ["Active", "Connected", "Core"]
	layer1 = np.asarray([new_active_all[-1], new_active_conn[-1], new_active_core[-1]])
	layer2 = np.asarray([unpaused_all[-1], unpaused_conn[-1], unpaused_core[-1]])
	layer3 = np.asarray([returned_all[-1], returned_conn[-1], returned_core[-1]])
	layer4 = np.asarray([continous_all[-1], continous_conn[-1], continous_core[-1]])
	
	bar_width = 0.35
	
	# plot results
	curr_ax.bar(mem_type_labels, layer4, bar_width, bottom=layer1+layer2+layer3, label='Continuous', color=act_type_colors[3])	
	curr_ax.bar(mem_type_labels, layer3, bar_width, bottom=layer1+layer2, label='Returned', color=act_type_colors[2])
	curr_ax.bar(mem_type_labels, layer2, bar_width, bottom=layer1, label='Unpaused', color=act_type_colors[1])
	curr_ax.bar(mem_type_labels, layer1, bar_width, label='New', color=act_type_colors[0])
	
	# add yaxis label
	curr_ax.set_ylabel('# Members')
	
	# add title
	curr_ax.set_title('Current period')
	
	# add legend
	curr_ax.legend()
	
	
	# # # RECENT HISTORY TABLE # # #
	
	# specify x tick labels
	x_tick_labels = ["All", "New", "Unp.", "Ret.", "Cont.", "Conn.", "Core"]
	
	# initiate subplot for last PAST_PER periods
	rec_ax = act_mem_fig.add_subplot(1,2,2)
	
	# make empty result matrix and array
	heatmap_mat = np.zeros((PER_TABLE,7))
	y_tick_labels = [""] * PER_TABLE
		
	# for each period that should be included in the heatmap
	for period in range(PER_TABLE):
				
		# add corresponding data to table
		heatmap_mat[period, 0] = new_active_all[-1-(period*WINDOW_D)] + \
			unpaused_all[-1-(period*WINDOW_D)] + returned_all[-1-(period*WINDOW_D)] \
			+ continous_all[-1-(period*WINDOW_D)]
		heatmap_mat[period, 1] = new_active_all[-1-(period*WINDOW_D)]
		heatmap_mat[period, 2] = unpaused_all[-1-(period*WINDOW_D)]
		heatmap_mat[period, 3] = returned_all[-1-(period*WINDOW_D)]
		heatmap_mat[period, 4] = continous_all[-1-(period*WINDOW_D)]
		heatmap_mat[period, 5] = new_active_conn[-1-(period*WINDOW_D)] + \
			unpaused_conn[-1-(period*WINDOW_D)] + returned_conn[-1-(period*WINDOW_D)] \
			+ continous_conn[-1-(period*WINDOW_D)]
		heatmap_mat[period, 6] = new_active_core[-1-(period*WINDOW_D)] + \
			unpaused_core[-1-(period*WINDOW_D)] + returned_core[-1-(period*WINDOW_D)] \
			+ continous_core[-1-(period*WINDOW_D)]
	
		# add ytick label to array
		y_tick_labels[period] = "P {}".format(-1*period)
		
	# make heatmap of results	
	heat_map = sns.heatmap(heatmap_mat, cmap="Greens", linewidth=1, annot=True, \
		xticklabels=x_tick_labels, yticklabels=y_tick_labels)
	
	# add title
	rec_ax.set_title('Last {} periods'.format(PER_TABLE))
	
	# move xtick label to above figure
	rec_ax.xaxis.tick_top()
	
	# rotate tick labels
	plt.xticks(rotation=90) 
	plt.yticks(rotation=0)
	
	
	# show figure
	if SHOW:
		act_mem_fig.tight_layout()
		plt.show()
		
	# save figure
	if SAVE_PATH != None:
		act_mem_fig.tight_layout()
		act_mem_fig.savefig(SAVE_PATH + "_recent.png")
		print("Engagement active members figure saved in " + SAVE_PATH + "_recent.png")
			
	
	# # # ALL HISTORY LINE PLOTS # # #
	
	# initiate second figure
	act_mem_hist_fig = plt.figure(figsize=(8,10))
	
	# specify labels for plots
	act_type_labels = ["New", "Unp.", "Ret.", "Cont."]
	
	
	# initiate subplot for all active history
	all_active_ax = act_mem_hist_fig.add_subplot(5,1,1)
	
	# plot stacked lineplot
	plot_stacked_range(new_active_all, unpaused_all, returned_all, \
		continous_all, act_type_labels, act_type_colors, date_tick_i, \
		date_tick_labels, PER_TABLE, WINDOW_D, all_active_ax)
		
	# add title
	all_active_ax.set_title('All active history')
	
	
	# initiate subplot for connected history
	all_conn_ax = act_mem_hist_fig.add_subplot(5,1,2)
	
	# plot stacked lineplot
	plot_stacked_range(new_active_conn, unpaused_conn, returned_conn, \
		continous_conn, act_type_labels, act_type_colors, date_tick_i, \
		date_tick_labels, PER_TABLE, WINDOW_D, all_conn_ax)
		
	# add title
	all_conn_ax.set_title('Connected history')
	
	
	# initiate subplot for periphery history
	all_per_ax = act_mem_hist_fig.add_subplot(5,1,3)
	
	# plot stacked lineplot
	plot_stacked_range(new_active_per, unpaused_per, returned_per, \
		continous_per, act_type_labels, act_type_colors, date_tick_i, \
		date_tick_labels, PER_TABLE, WINDOW_D, all_per_ax)
		
	# add title
	all_per_ax.set_title('Periphery history')
	
	
	# initiate subplot for core history
	all_core_ax = act_mem_hist_fig.add_subplot(5,1,4)
	
	# plot stacked lineplot
	plot_stacked_range(new_active_core, unpaused_core, returned_core, \
		continous_core, act_type_labels, act_type_colors, date_tick_i, \
		date_tick_labels, PER_TABLE, WINDOW_D, all_core_ax)
	
	# add title
	all_core_ax.set_title('Core history')
	
	
	# initiate subplot for non core history
	all_ncore_ax = act_mem_hist_fig.add_subplot(5,1,5)
	
	# plot stacked lineplot
	plot_stacked_range(new_active_ncore, unpaused_ncore, returned_ncore, \
		continous_ncore, act_type_labels, act_type_colors, date_tick_i, \
		date_tick_labels, PER_TABLE, WINDOW_D, all_ncore_ax)
	
	# add title
	all_ncore_ax.set_title('Non core history')
	
		
	# show figure
	if SHOW:
		act_mem_hist_fig.tight_layout()
		plt.show()
		
	# save figure
	if SAVE_PATH != None:
		act_mem_hist_fig.tight_layout()
		act_mem_hist_fig.savefig(SAVE_PATH + "_history.png")
		print("Engagement active members figure saved in " + SAVE_PATH + "_history.png")
		
	return act_mem_fig, act_mem_hist_fig


def plot_inactive_members(all_active, all_connected, all_paused, all_core, \
	all_new_disengaged, all_new_active, all_unpaused, all_returned, all_continous, PAUSED_T_THR, \
	date_tick_i, date_tick_labels, PER_TABLE, WINDOW_D, RAND, SHOW, SAVE_PATH=None):
	"""
	Plots inactive members graphs from engagement data
	
	Input:
	all_* - {str: set} : dictionary with all * account names for each
		analysis period
	PAUSED_T_THR - int : number of periods to be paused before being disengaged
	date_tick_i - [int] : dictionary key values that correspond to dates
		that should be plotted as tick labels for the plots
	date_tick_labels - [str] : dates corresponding to the date_tick_i indices
	PER_TABLE - int : number of periods shown in the table
	WINDOW_D - int : width of an analysis window in number of days
	RAND - bool : whether values should be randomized before plotting
	SHOW - bool : whether figure should be shown
	SAVE_PATH = str : path to where figure should be saved, existing figures
		 with same path are overwritten. Set to None to not save figure (default = None)
		 
	Output:
	inact_mem_fig - fig : figure object with recent inactivity data
	inact_mem_hist_fig - fig : figure object with history of inactivity data
	Plots and/or saves figure based on SHOW and SAVE_PATH values
	"""
	
	# terminate function if output should not be saved or shown
	if SAVE_PATH == None and not SHOW:
		return
		
		
	# # # GENERAL PREPARATIONS # # #
	
	# set activity type colors
	act_type_colors = ['#C85200', '#FF800E', '#FFBC79', '#CFCFCF']  # for: remainder, continuous, connected, core respectively
	
	# make an empty dictionary with same keys as all_active
	empty_dict = dict.fromkeys(all_active.keys(), set(""))
	
	
	# # # DIVIDE PAUSED # # #
	
	# initiate empty result lists
	all_remainder_paused = [None] * PAUSED_T_THR
	all_core_paused = [None] * PAUSED_T_THR
	all_conn_paused = [None] * PAUSED_T_THR
	all_cont_paused = [None] * PAUSED_T_THR
	all_paused_paused = [all_paused] + [None] * PAUSED_T_THR
		
	# for each period someone can be paused
	for p_per in range(PAUSED_T_THR):
		
		# obtain overlap between paused and paused in previous period 
		_, [all_remainder_paused[p_per], all_paused_paused[p_per+1]] = \
			assess_overlap(all_paused_paused[p_per], [empty_dict, all_paused], \
			len(all_active.keys()), (p_per+1)*WINDOW_D, True, RAND)
	
		# obtain overlap between remaining paused (so not paused previous period) and core in previous period 
		_, [all_remainder_paused[p_per], all_core_paused[p_per]] = \
			assess_overlap(all_remainder_paused[p_per], [empty_dict, all_core], \
			len(all_active.keys()), (p_per+1)*WINDOW_D, True, RAND)
			
		# obtain overlap between remaining paused (so not paused or core in previous period) and connected in previous period 
		_, [all_remainder_paused[p_per], all_conn_paused[p_per]] = \
			assess_overlap(all_remainder_paused[p_per], [empty_dict, all_connected], \
			len(all_active.keys()), (p_per+1)*WINDOW_D, True, RAND)
		
		# obtain overlap between remaining paused (so not paused, core or connected in previous period) and continuously active in previous period 
		_, [all_remainder_paused[p_per], all_cont_paused[p_per]] = \
			assess_overlap(all_remainder_paused[p_per], [empty_dict, all_continous], \
			len(all_active.keys()), (p_per+1)*WINDOW_D, True, RAND)
		
	# merge results into single sets and count
	n_core_paused, _ = merge_results(all_core_paused)
	n_conn_paused, _ = merge_results(all_conn_paused)
	n_cont_paused, _ = merge_results(all_cont_paused)
	n_rem_paused, _ = merge_results(all_remainder_paused)
	
	
	# # # DIVIDE DISENGAGED # # #	
	
	# obtain overlap between disengaged and core in last active period 
	[_, n_core_disengaged], [all_remainder_disengaged, _] = \
		assess_overlap(all_new_disengaged, [empty_dict, all_core], \
		len(all_active.keys()), (PAUSED_T_THR+1)*WINDOW_D, True, RAND)
	
	# obtain overlap between remaining disengaged (so not core) and connected in last active period 
	[_, n_conn_disengaged], [all_remainder_disengaged, _] = \
		assess_overlap(all_remainder_disengaged, [empty_dict, all_connected], \
		len(all_active.keys()), (PAUSED_T_THR+1)*WINDOW_D, True, RAND)
		
	# obtain overlap between remaining disengaged (so not core or connected) and continuously active in last active period 
	[n_rem_disengaged, n_cont_disengaged], _ = \
		assess_overlap(all_remainder_disengaged, [empty_dict, all_continous], \
		len(all_active.keys()), (PAUSED_T_THR+1)*WINDOW_D, True, RAND)	
			
	
	# # # PLOT CURRENT PERIOD BARPLOT # # #
	
	# initiate first figure
	inact_mem_fig = plt.figure(figsize=(8,3))
			
	# initiate subplot for current period
	curr_ax = inact_mem_fig.add_subplot(1,2,1)
	
	# specify what to plot
	mem_type_labels = ["Paused", "Disengaged",""]
	layer1 = np.asarray([n_rem_paused[-1], n_rem_disengaged[-1], 0])
	layer2 = np.asarray([n_cont_paused[-1], n_cont_disengaged[-1], 0])
	layer3 = np.asarray([n_conn_paused[-1], n_conn_disengaged[-1], 0])
	layer4 = np.asarray([n_core_paused[-1], n_core_disengaged[-1], 0])
	
	bar_width = 0.35
	
	# plot results	
	curr_ax.bar(mem_type_labels, layer4, bar_width, bottom=layer1+layer2+layer3, label='Core', color=act_type_colors[3])
	curr_ax.bar(mem_type_labels, layer3, bar_width, bottom=layer1+layer2, label='Connected', color=act_type_colors[2])
	curr_ax.bar(mem_type_labels, layer2, bar_width, bottom=layer1, label='Continuous', color=act_type_colors[1])
	curr_ax.bar(mem_type_labels, layer1, bar_width, label='Remainder', color=act_type_colors[0])
		
	# add yaxis label
	curr_ax.set_ylabel('# Members')
	
	# add title
	curr_ax.set_title('Current period')
	
	# add legend
	curr_ax.legend()
	
	
	# # # PLOT RECENT HISTORY TABLE # # #
	
	# specify x tick labels
	x_tick_labels = ["P. All", "P. Cont.", "P. Conn.", "P. Core", "D. All", "D. Cont.", "D. Conn.", "D. Core"]
	
	# initiate subplot for last PAST_PER periods
	rec_ax = inact_mem_fig.add_subplot(1,2,2)
	
	# make empty result matrix and array
	heatmap_mat = np.zeros((PER_TABLE,8))
	y_tick_labels = [""] * PER_TABLE
	
	
	# for each period that should be included in the heatmap
	for period in range(PER_TABLE):
				
		# add corresponding data to table
		heatmap_mat[period, 0] = n_rem_paused[-1-(period*WINDOW_D)] + \
			n_cont_paused[-1-(period*WINDOW_D)] + n_conn_paused[-1-(period*WINDOW_D)] \
			+ n_core_paused[-1-(period*WINDOW_D)]
		heatmap_mat[period, 1] = n_cont_paused[-1-(period*WINDOW_D)]
		heatmap_mat[period, 2] = n_conn_paused[-1-(period*WINDOW_D)]
		heatmap_mat[period, 3] = n_core_paused[-1-(period*WINDOW_D)]
		heatmap_mat[period, 4] = n_rem_disengaged[-1-(period*WINDOW_D)] + \
			n_cont_disengaged[-1-(period*WINDOW_D)] + n_conn_disengaged[-1-(period*WINDOW_D)] \
			+ n_core_disengaged[-1-(period*WINDOW_D)]
		heatmap_mat[period, 5] = n_cont_disengaged[-1-(period*WINDOW_D)]
		heatmap_mat[period, 6] = n_conn_disengaged[-1-(period*WINDOW_D)]
		heatmap_mat[period, 7] = n_core_disengaged[-1-(period*WINDOW_D)]
		
		# add ytick label to array
		y_tick_labels[period] = "P {}".format(-1*period)
		
	# make heatmap of results	
	heat_map = sns.heatmap(heatmap_mat, cmap="Greens", linewidth=1 , annot=True, \
		xticklabels=x_tick_labels, yticklabels=y_tick_labels)
	
	# add title
	rec_ax.set_title('Last {} periods'.format(PER_TABLE))
	
	# move xtick label to above figure
	rec_ax.xaxis.tick_top()
	
	# rotate tick labels
	plt.xticks(rotation=90) 
	plt.yticks(rotation=0)
	
	# show figure
	if SHOW:
		inact_mem_fig.tight_layout()
		plt.show()
		
	# save figure
	if SAVE_PATH != None:
		inact_mem_fig.tight_layout()
		inact_mem_fig.savefig(SAVE_PATH + "_recent.png")
		print("Engagement inactivating members figure saved in " + SAVE_PATH + "_recent.png")
	
	
	# # # PLOT ALL HISTORY LINE PLOTS # # #
	
	# initiate second figure
	inact_mem_hist_fig = plt.figure(figsize=(8,4))
	
	# specify labels for plots
	act_type_labels = ["Rem.", "Cont.", "Conn.", "Core."]
	
	
	# initiate subplot for all active history
	all_paused_ax = inact_mem_hist_fig.add_subplot(2,1,1)
	
	# plot stacked lineplot
	plot_stacked_range(n_rem_paused, n_cont_paused, n_conn_paused, \
		n_core_paused, act_type_labels, act_type_colors, date_tick_i, \
		date_tick_labels, PER_TABLE, WINDOW_D, all_paused_ax)
		
	# add title
	all_paused_ax.set_title('Paused history')
	
	
	# initiate subplot for connected history
	all_dis_ax = inact_mem_hist_fig.add_subplot(2,1,2)
	
	# plot stacked lineplot
	plot_stacked_range(n_rem_disengaged, n_cont_disengaged, n_conn_disengaged, \
		n_core_disengaged, act_type_labels, act_type_colors, date_tick_i, \
		date_tick_labels, PER_TABLE, WINDOW_D, all_dis_ax)
		
	# add title
	all_dis_ax.set_title('Disengaged history')
	

	# show figure
	if SHOW:
		inact_mem_hist_fig.tight_layout()
		plt.show()
		
	# save figure
	if SAVE_PATH != None:
		inact_mem_hist_fig.tight_layout()
		inact_mem_hist_fig.savefig(SAVE_PATH + "_history.png")
		print("Engagement inactivating members history figure saved in " + SAVE_PATH + "_history.png")
		
	return inact_mem_fig, inact_mem_hist_fig
	
	
# # # OTHER FUNCTIONS # # #

def plot_stacked_range(pl_layer1, pl_layer2, pl_layer3, pl_layer4, pl_lables, \
	pl_colors, date_tick_i, date_tick_labels, PER_TABLE, WINDOW_D, pl_ax):
	"""
	Plots stacked linegraph with number of members per engagement type
	
	Input:
	pl_layer* - [int] : number of members per analysis window for layer * of plot
	pl_lables - [str] : labels for the different engagement types
	pl_colors - [str] : colors for the different engagement types
	date_tick_i - [int] : dictionary key values that correspond to dates
		that should be plotted as tick labels for the plots
	date_tick_labels - [str] : dates corresponding to the date_tick_i indices
	PER_TABLE - int : number of periods shown in the table
	WINDOW_D - int : width of an analysis window in number of days
	
	Output:
	Plots figure in current axis
	"""
	
	# plot results as stacked plot
	plt.stackplot(range(len(pl_layer1)), pl_layer1, pl_layer2, pl_layer3, pl_layer4, \
		baseline="zero", labels=pl_lables, colors=pl_colors)
	
	# for each recent period
	for rec_per in range(PER_TABLE):
	
		# add indicator
		plt.axvline(len(pl_layer1)-1-(rec_per * WINDOW_D), ymin=0, ymax=1, color="k", dashes=(2,2))
	
	# add ylabel	
	pl_ax.set_ylabel('# Members')
	
	# add xtick labels
	plt.xticks(ticks = date_tick_i, labels = date_tick_labels)
	
	# adjust axes
	plt.xlim(0,len(pl_layer1)-1)
	
	
# # #
	
def merge_results(dict_list):
	"""
	Merges the sets under same key in different dictionaries
	
	Input:
	dict_list - [{str : set}] : list of all dictionaries of which the 
		sets under the same keys should be merged.
		
	Output:
	n_acc_out - [int] : list of the length of each set per key after merging
	dict_out - {str : set} : results after merging dictionary values
	
	Note:
	Only the keys of the first dictionary in dict_list are considered
	"""
		
	# get keys from first dict in list
	dict_keys_temp = [key for key in dict_list[0].keys()]
	
	# initiate empty result dict and list
	dict_out = {}
	n_acc_out = [0] * (int(dict_keys_temp[-1])+1)
	
	# for each dictionary key in first dictionary in list
	for key in dict_list[0].keys():
				
		# create empty set
		temp_set = set("")
		
		# for each dictionary
		for dic in dict_list:
			
			# add results for key to temp_set
			temp_set.update(dic[key])
		
		# store temp set in dictionary
		dict_out[key] = temp_set
			
		# store total number of accounts in list
		n_acc_out[int(key)] = len(temp_set)
		
	
	return n_acc_out, dict_out
	
	
# # #

def assess_overlap(ref_dict, comp_dicts, num_period, num_past, add_remainder, rand):
	""" 
	Assesses overlap between sets in different dictionaries
	
	Input:
	ref_dict - {str : set} : reference dictionary that comp_dicts are compared to
	comp_dicts - [{str : set}] : all comparison dictionaries
	num_period - int : number of periods into the past that sets in 
		comp_dicts should be selected from relative to ref_dict
	add_remainder - bool : whether the difference between the number of
		values under a ref_dict key and the sum of the number of values 
		under all corresponding comp_dicts keys should be added to the 
		first dictionary in comp_dicts
	rand - bool : whether the number of accounts in comp_out should
		be randomized before outputting the results
	
	Output:
	comp_out - [[int]] : list of lists with number of overlapping 
		accounts for each dictionary in comp_dicts relative to ref_dict
	comp_out - [{str : set}] : list of dictionaries with overlapping 
		accounts for each dictionary in comp_dicts relative to ref_dict	
	"""
		
	# initiate empty result lists for each comparison set
	comp_out = [[0] * num_period for _ in range(len(comp_dicts))]
	
	# initiate empty result list of dictionaries for each comparison set
	overlap_acc = [{} for _ in range(len(comp_dicts))]
	
	
	# for each time period
	for period in range(num_period):
				
		# if there is data for this time period
		if str(period) in ref_dict.keys():
			
			# define comparison period
			comp_per = str(period-num_past)
			
			# set total sum for period to 0
			tot_sum_per = 0
			
			# set total accounts to empty set
			tot_accounts = set("")
			
			# for each comparison dictionary
			for i, comp_dict in enumerate(comp_dicts):
					
				# if comparison period is present in keys
				if str(comp_per) in comp_dict.keys():
										
					# assess overlap
					overlap_acc[i][str(period)] = set(ref_dict[str(period)]).intersection(set(comp_dict[str(comp_per)]))					
					comp_out[i][period] = len(overlap_acc[i][str(period)])
										
					# add to total sum for this period
					tot_sum_per += len(overlap_acc[i][str(period)])
					
					# add accounts to total set for this period
					tot_accounts.update(overlap_acc[i][str(period)])
					
				else:
					
					# store empty set
					overlap_acc[i][str(period)] = set("")
					
						
			# obtain difference between total active and sum of types
			diff_act = len(ref_dict[str(period)]) - tot_sum_per
			
			# if the remainder of the accounts should be added to the first comp_dict category	
			if add_remainder:
				
				# obtain difference between total active and sum of types
				diff_act = len(ref_dict[str(period)]) - tot_sum_per	
							
				# add difference in number of accounts to first comp_dict category
				comp_out[0][period] += diff_act
			
				# add remaining accounts to first comp_dict category
				overlap_acc[0][str(period)].update(set(ref_dict[str(period)])-tot_accounts)
				
			if rand:
				
				# for each comparison set
				for i, _ in enumerate(comp_dicts):
				
					# add or subtract values randomly
					comp_out[i][period] += random.randint(-5, 5)
					
					# set values below 0 to 0
					if comp_out[i][period] < 0:
						comp_out[i][period] = 0
				
					
	return comp_out, overlap_acc
