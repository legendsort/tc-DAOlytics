#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compute_network.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 
 
# # # # # import libraries # # # # #

import sys
import os
import csv
import numpy as np
import networkx as nx
from datetime import datetime


# # # # # main function # # # # #

def compute_network(data, DIR, REMOVE_ACCOUNTS, MERGE_ACCOUNTS, SEL_RANGE, \
	EMOJI_TYPES, MEN_SUBSTRING, REACT_SUBSTRING, REPLY_SUBSTRING, \
	INTERACTION_WEIGHTS, TEMP_THREAD_DIR_PATH):
	"""
	Computes interaction network based on discord data in csv file
	
	Input:
	data - np array : loaded contents of (combined) csv file(s)
	DIR - bool : whether a directed network should be constructed
	REMOVE_ACCOUNTS - [str] : list of account names that should be 
		removed from the analysis
	MERGE_ACCOUNTS - [(str,str)] : list of tuples with account names 
		that should be merged in the analysis. Only the first account
		name in the tuple remains
	SEL_RANGE - [str,str] : list of two strings indicating start and 
		end time to include in analysis ('yy/mm/dd HH:MM:SS')
	EMOJI_TYPES - [str] or None : list of strings indicating which emoji
		types to consider (None = all emojis)
	MEN_SUBSTRING - [str] or None : only mentions in messages with a 
		substring in this list are considered (None = all messages)
	REACT_SUBSTRING - [str] or None : only reactions to messages with a 
		substring in this list are considered (None = all messages)
	REPLY_SUBSTRING - [str] or None : only replies to messages with a 
		substring in this list are considered (None = all messages)
	INTERACTION_WEIGHTS - [float/int, float/int, float/int, float/int] : 
		relative weights of mentions, reactions, replies and thread 
		interactions for computing the summed network
	TEMP_THREAD_DIR_PATH - str : path to directory where thread data 
		from different channels should be combined
	
	Output:
	for each type of network: 
	graph, sum, in_frac - (graph, 1D np.array, 1D np.array) : (the graph
		object, weighted degree, fraction of weighted in degree)
	acc_names - [str] : all active accounts
	"""
	
	# # # MAKE SELECTION OF MESSAGES BASED ON TIME # # #
	
	mess_indices = select_messages_time(data, SEL_RANGE)
	
	
	# # # MAKE SELECTION OF MESSAGES BASED ON EXCLUDED AUTHORS # # #
	
	mess_indices, mess_authors = exclude_specific_authors(data, mess_indices, REMOVE_ACCOUNTS)
	
	
	# # # MAKE SELECTION OF ALL ACTIVE AUTHORS # # #
		
	# extract emoji react authors for each message within time range (only first function output is used)
	emoji_authors = extract_unique_reactors(data[mess_indices,np.where(data[0,:]=="Reactions")])[0]
	
	# extract mentioned accounts (only first function output is used)
	men_accounts = extract_unique_mentioned(data[mess_indices, np.where(data[0,:]=="User_Mentions")])[0]
	
	# select all account names that have sent a message or emoji or are mentioned
	all_active = set(np.unique(mess_authors)).union(set(emoji_authors).union(set(men_accounts)))
			
	# remove account names in REMOVE_ACCOUNTS and sort remaining accounts alphabetically
	acc_names = np.sort(np.array(list(all_active - set(REMOVE_ACCOUNTS))))
		
		
	# # # CONSTRUCT MATRICES FOR MENTIONS, REACTIONS AND REPLIES # # #
	
	# create empty result matrices
	men_mat = np.zeros((len(acc_names), len(acc_names)))
	react_mat = np.zeros((len(acc_names), len(acc_names)))
	reply_mat = np.zeros((len(acc_names), len(acc_names)))
	
	# loop over each message from main channels
	for mess_i in mess_indices:
		
		# extract author of message
		mess_aut = data[mess_i,np.where(data[0,:]=="Author")][0]
				
		# determine index of author in acc_names
		aut_i = np.where(acc_names == mess_aut)[0]
		
		# extract content of message
		mess_cont = data[mess_i,np.where(data[0,:]=="Content")][0]
		
		# if message is default message
		if data[mess_i,np.where(data[0,:]=="Type")] == "DEFAULT":
		
			# if message contains specified substring (or None are specified)
			if (MEN_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in MEN_SUBSTRING])):
				
				# update mention matrix
				men_mat, _ = update_mention_matrix(men_mat, aut_i, data[mess_i,np.where(data[0,:]=="User_Mentions")], acc_names, DIR) 
			
			# if message contains specified substring (or None are specified)
			if (REACT_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in REACT_SUBSTRING])):
						
				# update emoji reaction matrix
				react_mat, _ = update_react_matrix(react_mat, aut_i, data[mess_i,np.where(data[0,:]=="Reactions")], acc_names, DIR, EMOJI_TYPES) 
			
		# if message is reply
		if data[mess_i,np.where(data[0,:]=="Type")] == "REPLY":
			
			# if message contains specified substring (or None are specified)
			if (REPLY_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in REPLY_SUBSTRING])):
				
				# update reply matrix
				reply_mat, _ = update_reply_matrix(reply_mat, aut_i, data[mess_i,np.where(data[0,:]=="Replied_User")][0][0], acc_names, DIR) 
			
			# if message contains specified substring (or None are specified)
			if (MEN_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in MEN_SUBSTRING])):
				
				# update mention matrix (reply interactor is excluded)
				men_mat, _ = update_mention_matrix(men_mat, aut_i, data[mess_i,np.where(data[0,:]=="User_Mentions")], acc_names, DIR, data[mess_i,np.where(data[0,:]=="Replied_User")][0][0]) 
				
			# if message contains specified substring (or None are specified)
			if (REACT_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in REACT_SUBSTRING])):
					
				# update emoji reaction matrix
				react_mat, _ = update_react_matrix(react_mat, aut_i, data[mess_i,np.where(data[0,:]=="Reactions")], acc_names, DIR)
	
		
	# # # CONSTRUCT MATRIX FOR THREADS # # #
	
	# make empty temporary result matrix
	thread_mat = np.zeros((len(acc_names), len(acc_names)))
			
	# obtain all file names in thread folder
	dir_names = os.listdir(TEMP_THREAD_DIR_PATH)
	
	# obtain file names of all csv files
	thread_files = [j for j in dir_names if ".csv" in j]
	
	
	# for each thread file
	for thr_file in thread_files:
				
		# # load thread data into numpy array
		# with open(TEMP_THREAD_DIR_PATH + "/" + thr_file, 'r') as x:
			# thr_data = np.array(list(csv.reader(x, delimiter=",")))
		
		
		# load channel data into numpy array
		with open(TEMP_THREAD_DIR_PATH + "/" + thr_file, 'r') as x:
			chan_data_obj = csv.reader(x, delimiter=",")
							
			# add content to array in less efficient way (TEMPORARY SOLUTION)
			for i, line in enumerate(chan_data_obj):
								
				# if line is the header
				if i == 0:
					
					# extract data
					thr_data = np.array(line)
						
					# extract number of columns for appending data
					num_col = len(thr_data)
				
				else:
																
					# if the line is the right size (likely "," in messages cause errors) and not the header
					if len(line) == num_col and i != 0:
							
						# store data of line
						thr_data = np.vstack((thr_data, np.array(line)))
		
					else:
						
						line = line[0].split(",")
						
						# if the line is the right size (likely "," in messages cause errors) and not the header
						if len(line) == num_col and i != 0:
							
							# store data of line
							thr_data = np.vstack((thr_data, np.array(line)))
						
			
		# if data only contains one message 
		if len(thr_data.shape) < 2:
			
			print("Thread had no data")
			
			# skip this itteration
			continue
			
		# select messages within SEL_RANGE		
		thr_mess_indices = select_messages_time(thr_data, SEL_RANGE)
			
		# remove messages from accounts in REMOVE_ACCOUNTS
		thr_mess_indices, thr_mess_authors = exclude_specific_authors(thr_data, thr_mess_indices, REMOVE_ACCOUNTS)
			
			
		# if data only contains one message or less
		if len(thr_mess_indices) < 2:
			
			# skip this itteration
			continue
			
			
		# extract emoji react authors for each message within time range (only first function output is used)
		thr_emoji_authors, thr_reacts_per_acc = extract_unique_reactors(thr_data[thr_mess_indices,np.where(thr_data[0,:]=="Reactions")])
	
		# extract mentioned accounts (only first function output is used)
		thr_men_accounts, thr_mens_per_acc = extract_unique_mentioned(thr_data[thr_mess_indices, np.where(thr_data[0,:]=="User_Mentions")])
	
		# select all account names that have sent a message or emoji or are mentioned
		thr_all_active = set(np.unique(thr_mess_authors)).union(set(thr_emoji_authors).union(set(thr_men_accounts)))
			
		# remove account names in REMOVE_ACCOUNTS and sort remaining accounts alphabetically
		thr_acc_names = np.sort(np.array(list(thr_all_active - set(REMOVE_ACCOUNTS))))
		
		
		# update thread matrix
		thread_mat = update_thread_matrix(thread_mat, acc_names, thr_acc_names, \
			thr_mess_authors, thr_reacts_per_acc, thr_emoji_authors, thr_mens_per_acc, thr_men_accounts)
			
									
	# # # MERGE SPECIFIED ACCOUNTS # # #
	
	# for each merge
	for mer in MERGE_ACCOUNTS:
				
		# merge account names
		men_mat, all_merged = merge_accounts_mat(men_mat, acc_names, mer)
		react_mat, all_merged = merge_accounts_mat(react_mat, acc_names, mer)
		reply_mat, all_merged = merge_accounts_mat(reply_mat, acc_names, mer)
		thread_mat, all_merged = merge_accounts_mat(thread_mat, acc_names, mer)
		
		# make mask to remove merged accounts
		mask = np.ones_like(acc_names, dtype=bool)
		mask[all_merged] = False
		
		# remove merged accounts from acc_names
		acc_names = acc_names[mask]


	# # # print account names in order # # #
	
	# # for each account name
	# for i, name in enumerate(acc_names):
		
		# # split account number of name
		# [split_name, account_num] = name.split("#")
		
		# #print("{} = {}".format(i, split_name))
		# print(name)	
		
	# # # SUM DIFFERENT NETWORK TYPES AND STORE AS GRAPH # # #
	
	# make weighted sum of all matrices (mentions, reactions, replies and threads)
	total_mat = INTERACTION_WEIGHTS[0] * men_mat + INTERACTION_WEIGHTS[1] \
		* react_mat + INTERACTION_WEIGHTS[2] * reply_mat + INTERACTION_WEIGHTS[3] * thread_mat
		
	# store all matrices as graphs
	men_graph = make_graph(men_mat,DIR)
	react_graph = make_graph(react_mat,DIR)
	reply_graph = make_graph(reply_mat,DIR)
	thread_graph = make_graph(thread_mat,DIR)
	total_graph = make_graph(total_mat,DIR)
	
		
	# # # COUNT NUMBER OF INTERACTIONS PER ACCOUNT # # #
		
	# count number of interactions per account for each network
	[sum_men, in_frac_men] = in_out_dir(men_mat,DIR)
	[sum_react, in_frac_react] = in_out_dir(react_mat,DIR)
	[sum_reply, in_frac_reply] = in_out_dir(reply_mat,DIR)
	[sum_thread, in_frac_thread] = in_out_dir(thread_mat,DIR)
	[sum_total, in_frac_total] = in_out_dir(total_mat,DIR)
			
	return [(total_graph, sum_total, in_frac_total), (men_graph, sum_men, in_frac_men), \
		(react_graph, sum_react, in_frac_react), (reply_graph, sum_reply, in_frac_reply), \
		(thread_graph, sum_thread, in_frac_thread), acc_names]


# # # # # nested functions # # # # #

def select_messages_time(data, SEL_RANGE):
	"""
	Makes selection of messages based on time they were sent
	
	Input:
	data - np array : loaded contents of (combined) csv file(s)
	SEL_RANGE - [str,str] : list of two strings indicating start and 
		end time to include in analysis ('yy/mm/dd HH:MM:SS')
	
	Output:
	mess_indices - [int] : list of index values for messages to be 
		considered for downstream analysis (messages sent during times
		outside of SEL_RANGE are removed)
	"""
	
	# extract message creation times
	mess_times = data[1:,np.where(data[0,:]=="Created_At")[0][0]].astype(int)
		
	# convert selection range dates to time
	sel_start = datetime.strptime(SEL_RANGE[0], '%y/%m/%d %H:%M:%S')
	sel_end = datetime.strptime(SEL_RANGE[1], '%y/%m/%d %H:%M:%S')
	
	# make empty result array
	mess_indices = np.asarray([])
	
	# for each message time
	for i,t in enumerate(mess_times):
			
		# convert to date time format and add to list
		mess_date_time = datetime.fromtimestamp(t/1000)
		
		# if message was sent within specified range
		if (mess_date_time >= sel_start) & (mess_date_time < sel_end):
			
			# store index of message for analysis
			mess_indices = np.append(mess_indices, i+1) # +1 to account for header row in data
	
	# change to integer array
	mess_indices = mess_indices.astype('int')
	
	return mess_indices
	
# # #

def exclude_specific_authors(data, mess_indices, REMOVE_ACCOUNTS):
	"""
	Makes selection of messages based authors that should be removed
	
	Input:
	data - np array : loaded contents of (combined) csv file(s)
	mess_indices - [int] : list of index values for messages to be 
		considered for downstream analysis
	REMOVE_ACCOUNTS - [str] : list of account names that should be 
		removed from the analysis
		
	Output:
	mess_indices - [int] : list of index values for messages to be 
		considered for downstream analysis (messages from authors in
		REMOVE_ACCOUNTS are removed)
	mess_authors - [str] : authors of all messages
	"""
	
	# extract message authors for each message within time range
	mess_authors = data[mess_indices,np.where(data[0,:]=="Author")]
	
	# make mask for messages that were sent from accounts not in REMOVE_ACCOUNTS
	mask = [x not in REMOVE_ACCOUNTS for x in mess_authors[0]]
	
	# select message indices that were sent within time range from accounts not in REMOVE_ACCOUNTS
	mess_indices = mess_indices[mask]
	
	return mess_indices, mess_authors
	
# # #

def extract_unique_reactors(react_data):
	"""
	Parses all unique account names from discord emoji reaction data
	
	Input:
	react_data - [str] : discord emoji reaction data (from csv file)
	
	Output:
	unique_acc_names - [str] : all unique account names that reacted 
		with an emoji
	reacts_per_acc - [float] : number of emoji reactions per account
	"""
	
	# make empty result lists
	unique_acc_names = []
	reacts_per_acc = []
	
	# for each response
	for resp in react_data[0]:
		
		# split data of different emoji responses
		resp_split = resp.split("&")
		
		# for each emoji
		for emoji in resp_split:
			
			# split different accounts that responded with emoji
			emoji_split = emoji.split(",")
			
			# for each account
			for acc in emoji_split[:-1]:
				
				# if account is not in result list yet
				if not acc in unique_acc_names:
					
					# add account to result lists
					unique_acc_names.append(acc)
					reacts_per_acc.append(1)
					
				else:
					
					# find index of account in list
					acc_i = unique_acc_names.index(acc)
									
					# add 1 to number of reactions per account
					reacts_per_acc[acc_i] += 1
					
	return unique_acc_names, reacts_per_acc
		
# # #

def extract_unique_mentioned(mention_data):
	"""
	Parses all unique account names from discord mention data
	
	Input:
	mention_data - [str] : discord account mention data (from csv file)
	
	Output:
	unique_acc_names - [str] : all unique account names that are
		mentioned in a message
	mens_per_acc - [float] : number of emoji reactions per account
	"""
	
	# make empty result lists
	unique_acc_names = []
	mens_per_acc = []
	
	# for each mention
	for men in mention_data[0]:
		
		# if an account is mentioned
		if len(men) > 0:
			
			# split data of different mentioned accounts
			men_split = men.split(",")
			
			# for each mentioned account
			for acc in men_split:
			
				# if account is not in result list yet
				if not acc in unique_acc_names:
					
					# add account to result lists
					unique_acc_names.append(acc)
					mens_per_acc.append(1)
						
				else:
						
					# find index of account in list
					acc_i = unique_acc_names.index(acc)
										
					# add 1 to number of reactions per account
					mens_per_acc[acc_i] += 1
	
	return unique_acc_names, mens_per_acc
# # #

def update_mention_matrix(mat, author_i, all_mentioned, acc_names, directed, not_valid=None):
	"""
	Updates the mention interaction matrix
	
	Input:
	mat - np.array : interaction matrix that needs to be updated
	author_i - int : index of message author in acc_names
	all_mentioned - str : all mentioned account names in a message (from csv file)
	acc_names - [str] : all active account names 
	directed - bool : whether a directed network should be constructed
	not_valid - [str] or None : list of account names that should not be considered (default = None)
	
	Output:
	mat - np.array: updated interaction matrix
	n_int - int: number of interactions added to matrix
	"""
	
	# set number of interactions to 0
	n_int = 0
	
	# split interactors (comma separated)
	mentioned_split = all_mentioned[0][0].split(",")

	# for each interaction
	for mentioned in mentioned_split:
				
		# if mentioned account is acc_names and not in not_valid
		if (mentioned in acc_names) & ((not_valid == None) or (mentioned not in not_valid)): 
									
			# determine index of interactor in acc_names
			mentioned_i = np.where(acc_names == mentioned)[0]
			
			# if the author is not the interactor
			if author_i != mentioned_i:
									
				# add 1 to corresponding edge in matrix
				if directed == False:
					mat[max([author_i, mentioned_i]), min([author_i, mentioned_i])] += 1
				else:
					mat[author_i, mentioned_i] += 1
				
				# add 1 to number of interactions
				n_int += 1
				
	return mat, n_int
	
# # #

def update_react_matrix(mat, author_i, all_reactors, acc_names, directed, emoji_types=None):
	"""
	Updates the reaction interaction matrix
	
	Input:
	mat - np.array : interaction matrix that needs to be updated
	author_i - int : index of message author in acc_names
	all_reactors - str : all accounts that reacted with an emoji and which emoji they reacted with (from csv file)
	acc_names - [str] : all active account names 
	directed - bool : whether a directed network should be constructed
	emoji_types - [str] or None : list of strings indicating which emoji types to consider (None = all emojis = default)
	
	Output:
	mat - np.array: updated interaction matrix
	n_int - int: number of interactions added to matrix
	"""
		
	# set number of interactions to 0
	n_int = 0
	
	# split interactors (& separated)
	first_split = all_reactors[0][0].split("&")
	
	for spl in first_split:
		
		# if spl is not empty
		if spl:
			
			# split interactor(s) and emoji (comma separated)
			second_split = spl.split(",")
			emoji = second_split[-1]
			reactors = second_split[:-1]
				
			for reactor in reactors:
						
				# if reacting account is in acc_names and reacted emoji is part of emoji_types if defined
				if (reactor in acc_names) & ((emoji_types == None) or (emoji in emoji_types)):
									
					# determine index of interactor in acc_names
					reactor_i = np.where(acc_names == reactor)[0]
						
					# if the author is not the interactor
					if author_i != reactor_i:
						
						# add 1 to corresponding edge in matrix
						if directed == False:
							mat[max([author_i, reactor_i]), min([author_i, reactor_i])] += 1
						else:
							mat[reactor_i, author_i] += 1
							
						# add 1 to number of interactions
						n_int += 1	
			
	return mat, n_int

# # #

def update_reply_matrix(mat, author_i, replier, acc_names, directed):
	"""
	Updates the reply interaction matrix
	
	Input:
	mat - np.array : interaction matrix that needs to be updated
	author_i - int : index of message author in acc_names
	replier - str : account that replied to a message (from csv file)
	acc_names - [str] : all active account names 
	directed - bool : whether a directed network should be constructed
	
	Output:
	mat - np.array: updated interaction matrix
	n_int - int: number of interactions added to matrix
	"""
	
	# set number of interactions to 0
	n_int = 0
	
	# determine index of interactor in acc_names
	replier_i = np.where(acc_names == replier)[0]
			
	# if the author is not the interactor
	if author_i != replier_i:
									
		# add 1 to corresponding edge in matrix
		if directed == False:
			mat[max([author_i, replier_i]), min([author_i, replier_i])] += 1
		else:
			mat[replier_i, author_i] += 1
			
		# add 1 to number of interactions
		n_int += 1
			
	return mat, n_int
	
# # #

def update_thread_matrix(mat, acc_names, thr_acc_names, thr_mess_authors, \
	thr_reacts_per_acc, thr_emoji_authors, thr_mens_per_acc, thr_men_accounts):
	"""
		update_thread_matrix(thr_acc_names, \
			thr_mess_authors, thr_reacts_per_acc, thr_emoji_authors, thr_mens_per_acc, thr_men_accounts)
	"""
	
	# obtain total number of active members
	n_mem = len(thr_acc_names)	
	
	# if thread has no activity to be analysed
	if n_mem < 2:
		return mat
			
	# make empty temporary result matrix
	temp_mat = np.zeros_like(mat)
				
	# make empty result arrays for interactions per member for all acc_names (including those not active in specific thread)
	n_mess_mem = np.zeros(len(acc_names))
	n_react_mem = np.zeros(len(acc_names))
	n_men_mem = np.zeros(len(acc_names))
		
	# for each member
	for i, mem in enumerate(acc_names):
			
		# count number of messages sent by member and store
		n_mess_mem[i] = int((thr_mess_authors==mem).sum())
			
		# if member has sent at least one emoji reaction
		if mem in thr_emoji_authors:
				
			# find number of reactions sent by member and store
			n_react_mem[i] = int(thr_reacts_per_acc[thr_emoji_authors.index(mem)])
				
		else:
				
			# set number of reactions sent by member to 0
			n_react_mem[i] = 0
				
		# if member is at least mentioned once
		if mem in thr_men_accounts:
				
			# find number of mentions for member and store
			n_men_mem[i] = int(thr_mens_per_acc[thr_men_accounts.index(mem)])
				
		else:
				
			# set number of reactions sent by member to 0
			n_men_mem[i] = 0
				
			
	# # compute metrics to assign connections for thread mat
				
	# obtain total number of messages sent in thread
	n_mess_tot = np.sum(n_mess_mem)
		
	# obtain total number of emoji reactions sent in thread
	n_react_tot = np.sum(n_react_mem)
		
	# compute total number of thread interactions 
	# (Threads are considered replies to a group. Mentions in replies
	# are not considered as additional interactions. Therefore, 
	# mentions are not considered as additional thread interactions)
	total_thr_int = (n_mess_tot  + n_react_tot) * (n_mem-1)

	# compute total number of interactions per member
	n_int_mem = n_mess_mem + n_react_mem + n_men_mem 
		
	# compute total member interactions (mentions are considered as additional member interactions)
	total_mem_int = np.sum(n_int_mem)
	
	# make copy of all account names
	copy_acc_names = acc_names
		
	# for each account name
	for acc_A_i, acc_A in enumerate(acc_names):
			
		# remove from copy
		copy_acc_names = np.delete(copy_acc_names, np.where(copy_acc_names==acc_A)[0])
			
		# for each comparison account name
		for acc_B in copy_acc_names:
				
			# obtain index of acc_B in acc_names
			acc_B_i = np.where(acc_names==acc_B)[0]
				
			# compute relative weight of total edge
			rel_edge = (n_int_mem[acc_A_i] / total_mem_int) * (n_int_mem[acc_B_i] / total_mem_int)
				
			# if relative edge is larger than 0
			if rel_edge > 0:
					
				# compute ratio between activity account A compared to B
				ratio_AB = n_int_mem[acc_A_i]/n_int_mem[acc_B_i]
					
				# update matrix with activity
				temp_mat[acc_A_i, acc_B_i] = rel_edge - (rel_edge/(ratio_AB+1)) 
				temp_mat[acc_B_i, acc_A_i] = rel_edge/(ratio_AB+1)
					
	# obtain sum of all edges
	edge_sum = np.sum(temp_mat, axis=None)
	
	if edge_sum > 0:
					
		# compute multiplication factor for matrix based on total interactions
		mult_fac = total_thr_int/edge_sum
								
		# multiply matrix so that it reflects total number of interactions
		temp_mat = temp_mat * mult_fac
			
		# add temp_mat to original matrix
		mat = mat+temp_mat
	
	return mat
	
# # #

def merge_accounts_mat(mat, acc_names, mer):
	"""
	sums the data from two or more selected account names
	
	Input:
	mat - np.array : interaction matrix
	acc_names - [str] : all active account names 
	mer - (str,str) : account names that should be merged (only first remains)
	
	Output:
	mat - np.array : interaction matrix after merging
	all_merged - [int] : index numbers in acc_names of removed accounts
	
	Notes:
	Interactions between account names that are merged are set to 0
	"""
	
	# make empty result list for all merged accounts
	all_merged = []
	
	# obtain index of account name that should remain
	remain_acc_name_i = np.where(acc_names == mer[0])[0]
	
	# return if the remaining account name is not present in acc_names
	if not remain_acc_name_i:
		return mat, all_merged
		
	# for each other account name
	for o_acc in range(1,len(mer)):
		
		# break out of itteration if other account name is not in acc_names
		if not mer[o_acc] in acc_names:
			break

		# obtain index of account name that gets merged
		mer_acc_name_i = np.where(acc_names == mer[o_acc])[0][0]
		
		# add values to account name that remains
		mat[remain_acc_name_i[0],:] += mat[mer_acc_name_i,:]
		mat[:,remain_acc_name_i[0]] += mat[:,mer_acc_name_i]
		
		# remove interactions between merged accounts
		mat[remain_acc_name_i[0],remain_acc_name_i[0]] = 0
		
		# add merged account index to list
		all_merged.append(mer_acc_name_i)
	
	# create mask to remove merged accounts from matrix
	mask = np.ones_like(mat, dtype=bool)
	mask[all_merged,:] = False	
	mask[:,all_merged] = False	
	
	# remove merged accounts from matrix
	mat = np.reshape(mat[mask], (-1, mask.shape[0]-len(all_merged)))
			
	return mat, all_merged

# # #

def make_graph(mat,directed):
	"""
	Turns interaction matrix into graph object
	
	Input:
	mat - np.array : interaction matrix
	directed - bool : whether an directed or undirected network should be constructed
	
	Output:
	graph - graph object: interaction graph
	"""
	
	# if network is directed
	if directed == True:
		
		# make empty result matrix
		new_mat = np.zeros_like(mat)
				
		# for each row
		for r in range(np.shape(mat)[0]):
			
			# for each column
			for c in range(r):
				
				# sum (r,c) and (c,r) values and store
				new_mat[r,c] = mat[r,c] + mat[c,r]
		
		# turn matrix into graph	
		graph = nx.from_numpy_array(new_mat)
		
	else:
		
		# turn matrix into graph	
		graph = nx.from_numpy_array(mat)
		
	return graph
		
# # #

def in_out_dir(mat, directed):
	"""
	Computes weighted degree and in vs out ratio for interaction matrix
	
	Input:
	mat - 2D np.array : interaction matrix
	directed - bool : whether the matrix is directed or undirected
	
	Output:
	tot_sum - 1D np.array : total sum of interactions (weighted degree) per account
	in_frac - 1D np.array : fraction of incoming interactions per account (In-Out)/tot
	"""
	
	if directed == True:
	
		# sum number of incoming interactions
		in_sum = np.sum(mat, 0)
	
		# sum number of outgoing interactions
		out_sum = np.sum(mat, 1)
	
		# sum total number of interactions
		tot_sum = in_sum+out_sum
	
		# compute fraction of incoming versus outgoing interactions
		in_frac = (in_sum-out_sum)/(tot_sum)
				
		# set all nan values to 0
		in_frac[np.isnan(in_frac)] = 0
		
	else:
		
		# sum total number of interactions
		tot_sum = np.sum(mat, 0) + np.sum(mat, 1)
		
		# set fraction of incoming versus outgoing interactions to 0
		in_frac = np.zeros_like(tot_sum)

	return(tot_sum, in_frac)
		 
