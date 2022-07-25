#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_network.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 
 
# # # # # import libraries # # # # #

import sys
import numpy as np
import networkx as nx
import csv


# # # # # main function # # # # #

def compute_network(FILENAME, DIR, REMOVE_ACCOUNTS, SEL_RANGE, EMOJI_TYPES, \
	MEN_SUBSTRING, REACT_SUBSTRING, REPLY_SUBSTRING, INTERACTION_WEIGHTS):
	"""
	Computes interaction network based on discord data in csv file
	
	Input:
	FILENAME - str : name of file with discord data (add path if stored 
		in different directory than main function)
	DIR - bool : whether a directed network should be constructed
	REMOVE_ACCOUNTS - [str] : list of account names that should be 
		removed from the analysis
	SEL_RANGE - [int,int] : list of two integers indicating start and 
		end time to include in analysis (inclusive)
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
	
	Output:
	for each type of network: 
	graph, sum, in_frac - (graph, 1D np.array, 1d np.array) : (the graph
		object, weighted degree, fraction of weighted in degree)
	acc_names - [str] : all active accounts
	"""
	
	# # # LOAD DATA # # #
	
	# load discord data into numpy array
	with open(FILENAME, 'r') as x:
		data = list(csv.reader(x, delimiter=","))
	data = np.array(data)
	
	
	# # # MAKE SELECTION OF MESSAGES BASED ON TIME # # #
	
	# extract message creation times
	mess_times = data[1:,np.where(data[0,:]=="Created_At")].astype(int)
	
	# select message indices that fall within range (+1 to account for header)
	mess_indices = 1 + np.where((mess_times >= SEL_RANGE[0]) & (mess_times <= SEL_RANGE[1]))[0]
	
	
	# # # MAKE SELECTION OF MESSAGES BASED ON EXCLUDED AUTHORS # # #
	
	# extract message authors for each message within time range
	mess_authors = data[mess_indices,np.where(data[0,:]=="Author")]
			
	# make mask for messages that were sent from accounts not in REMOVE_ACCOUNTS
	mask = [x not in REMOVE_ACCOUNTS for x in mess_authors[0]]
	
	# select message indices that were sent within time range from accounts not in REMOVE_ACCOUNTS
	mess_indices = mess_indices[mask]
	
	
	# # # MAKE SELECTION OF ALL ACTIVE AUTHORS # # #
		
	# extract emoji react authors for each message within time range
	emoji_authors = extract_unique_reactors(data[mess_indices,np.where(data[0,:]=="Reactions")])
	
	# select all account names that have sent a message or emoji
	all_active = set(np.unique(mess_authors)).union(set(emoji_authors))
			
	# remove account names in REMOVE_ACCOUNTS and sort remaining accounts alphabetically
	acc_names = np.sort(np.array(list(all_active - set(REMOVE_ACCOUNTS))))
	
	# print all account names in order
	for i, name in enumerate(acc_names):
		
		# split account number of name
		[split_name, account_num] = name.split("#")
		
		print("{} = {}".format(i, split_name))
		
		
	# # # CONSTRUCT MATRICES FOR EACH TYPE OF INTERACTION # # #
	
	# create empty result matrices
	men_mat = np.zeros((len(acc_names), len(acc_names)))
	react_mat = np.zeros((len(acc_names), len(acc_names)))
	reply_mat = np.zeros((len(acc_names), len(acc_names)))
	thread_mat = np.zeros((len(acc_names), len(acc_names)))
	
	# loop over each message
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
				men_mat = update_mention_matrix(men_mat, aut_i, data[mess_i,np.where(data[0,:]=="User_Mentions")], acc_names, DIR) 
			
			# if message contains specified substring (or None are specified)
			if (REACT_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in REACT_SUBSTRING])):
						
				# update emoji reaction matrix
				react_mat = update_react_matrix(react_mat, aut_i, data[mess_i,np.where(data[0,:]=="Reactions")], acc_names, DIR, EMOJI_TYPES) 
			
		# if message is reply
		if data[mess_i,np.where(data[0,:]=="Type")] == "REPLY":
			
			# if message contains specified substring (or None are specified)
			if (REPLY_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in REPLY_SUBSTRING])):
				
				# update reply matrix
				reply_mat = update_reply_matrix(reply_mat, aut_i, data[mess_i,np.where(data[0,:]=="Replied_User")][0][0], acc_names, DIR) 
			
			# if message contains specified substring (or None are specified)
			if (MEN_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in MEN_SUBSTRING])):
				
				# update mention matrix (reply interactor is excluded)
				men_mat = update_mention_matrix(men_mat, aut_i, data[mess_i,np.where(data[0,:]=="User_Mentions")], acc_names, DIR, data[mess_i,np.where(data[0,:]=="Replied_User")][0][0]) 
				
			# if message contains specified substring (or None are specified)
			if (REACT_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in REACT_SUBSTRING])):
					
				# update emoji reaction matrix
				react_mat = update_react_matrix(react_mat, aut_i, data[mess_i,np.where(data[0,:]=="Reactions")], acc_names, DIR)
			
		# if message is start of thread
		if data[mess_i,np.where(data[0,:]=="Type")] == "THREAD_CREATED":
			
			# TODO add thread interactions
			temp = 0
			
	
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
	
	# !!!!! REMOVE ONCE THREAD DATA IS COMPUTED
	thread_mat = men_mat
	sum_thread = sum_men
	in_frac_thread = in_frac_men
	
	return [(total_graph, sum_total, in_frac_total), (men_graph, sum_men, in_frac_men), \
		(react_graph, sum_react, in_frac_react), (reply_graph, sum_reply, in_frac_reply), \
		(thread_mat, sum_thread, in_frac_thread), acc_names]

# # # # # nested functions # # # # #

def extract_unique_reactors(react_data):
	"""
	Parses all unique account names from discord emoji reaction data
	
	Input:
	react_data - [str] : discord emoji reaction data (from csv file)
	
	Output:
	unique_acc_names - [str] : all unique account names that reacted 
		with an emoji
	"""
	
	# make empty result list
	unique_acc_names = []
	
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
					
					# add account to result list
					unique_acc_names.append(acc)
			
	return unique_acc_names
		
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
	"""
	
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
			
	return mat
	
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
	"""
		
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
			
	return mat

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
	"""
	
	# determine index of interactor in acc_names
	replier_i = np.where(acc_names == replier)[0]
			
	# if the author is not the interactor
	if author_i != replier_i:
									
		# add 1 to corresponding edge in matrix
		if directed == False:
			mat[max([author_i, replier_i]), min([author_i, replier_i])] += 1
		else:
			mat[replier_i, author_i] += 1
			
	return mat
	
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
		 
