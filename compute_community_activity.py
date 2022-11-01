#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compute_community_activity.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 
 
# # # # # import libraries # # # # #

import sys
import os
import csv
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

import compute_network


# # # # # main function # # # # #

def compute_community_activity(data, REMOVE_ACCOUNTS, MERGE_ACCOUNTS, SEL_RANGE, \
	EMOJI_TYPES, MESS_SUBSTRING, DAY_HIST, TEMP_THREAD_DIR_PATH):
	"""
	Counts community interaction based on discord data in csv file
	
	Input:
	data - np array : loaded contents of (combined) csv file(s)
	REMOVE_ACCOUNTS - [str] : list of account names that should be 
		removed from the analysis
	MERGE_ACCOUNTS - [(str,str)] : list of tuples with account names 
		that should be merged in the analysis. Only the first account
		name in the tuple remains
	SEL_RANGE - [str,str] : list of two strings indicating start and 
		end time to include in analysis ('yy/mm/dd HH:MM:SS')
	EMOJI_TYPES - [str] or None : list of strings indicating which emoji
		types to consider (None = all emojis)
	MESS_SUBSTRING - [str] or None : only messages with a substring in
		this list are considered (None = all messages)
	DAY_HIST - float/int : number of days into the past to consider for
		hourly activity data
	TEMP_THREAD_DIR_PATH - str : path to directory where thread data 
		from different channels should be combined
	
	Output:
	*_range - [int] : range of number of * per day over SEL_RANGE
	*_hourly - 7x24 [int] : hourly number of * summed over the last 
		DAY_HIST days
	*_per_account - [int] : number of * per account summed over the last
		DAY_HIST days
	acc_names - [str] : account names of all active members (message, 
		emoji, mentioned) in data over SEL_RANGE. Has same order as 
		*_per_account
	"""
	
	# # # MAKE SELECTION OF MESSAGES BASED ON TIME # # #
	
	mess_indices = compute_network.select_messages_time(data, SEL_RANGE)
	
	
	# # # MAKE SELECTION OF MESSAGES BASED ON EXCLUDED AUTHORS # # #
	
	mess_indices, mess_authors = compute_network.exclude_specific_authors(data, mess_indices, REMOVE_ACCOUNTS)
	
	
	# # # MAKE SELECTION OF ALL ACTIVE AUTHORS # # #
		
	# extract emoji react authors for each message within time range (only first function output is used)
	emoji_authors = compute_network.extract_unique_reactors(data[mess_indices,np.where(data[0,:]=="Reactions")])[0]
	
	# extract mentioned accounts (only first function output is used)
	men_accounts = compute_network.extract_unique_mentioned(data[mess_indices, np.where(data[0,:]=="User_Mentions")])[0]
	
	# select all account names that have sent a message or emoji or are mentioned
	all_active = set(np.unique(mess_authors)).union(set(emoji_authors).union(set(men_accounts)))
			
	# remove account names in REMOVE_ACCOUNTS and sort remaining accounts alphabetically
	acc_names = np.sort(np.array(list(all_active - set(REMOVE_ACCOUNTS))))
	
	
	# # # DEFINE ANALYSIS RANGE # # #
	
	# determine window start times
	start_dt = datetime.strptime(SEL_RANGE[0], '%y/%m/%d %H:%M:%S')
	end_dt = datetime.strptime(SEL_RANGE[1], '%y/%m/%d %H:%M:%S')
	
	time_diff = end_dt - start_dt
	
	# determine first time to consider for hourly history
	last_hourly_hist = end_dt - relativedelta(days=DAY_HIST)
	
	
	# # # # RESULT ARRAYS # # #
	
	# initiate empty result arrays		
	mess_range = np.zeros(time_diff.days)
	int_range = np.zeros(time_diff.days)
	emoji_range = np.zeros(time_diff.days)
	
	mess_hourly = np.zeros((7,24))
	int_hourly = np.zeros((7,24))
	emoji_hourly = np.zeros((7,24))
	
	mess_per_acc = np.zeros((1,len(acc_names)))[0]
	men_per_acc = np.zeros((1,len(acc_names)))[0]
	rep_per_acc = np.zeros((1,len(acc_names)))[0]
	emoji_per_acc = np.zeros((1,len(acc_names)))[0]
	thr_per_acc = np.zeros((1,len(acc_names)))[0]
	int_per_acc = np.zeros((1,len(acc_names)))[0] 	
		
		
	# # # ANALYSIS MAIN CHANNEL DATA  # # #
	
	# obtain message, interaction and emoji times for main channel data
	mess_range, int_range, emoji_range, mess_hourly, int_hourly, emoji_hourly, mess_per_acc, \
		men_per_acc, rep_per_acc, emoji_per_acc, thr_per_acc, int_per_acc = \
		analyse_mess_times(mess_range, int_range, emoji_range, mess_hourly, int_hourly, \
		emoji_hourly, mess_per_acc, men_per_acc, rep_per_acc, emoji_per_acc, thr_per_acc, \
		int_per_acc, data, mess_indices, start_dt, end_dt, last_hourly_hist, \
		acc_names, False, MESS_SUBSTRING, EMOJI_TYPES) 
		
		
	# # # LOAD THREAD DATA # # #
			
	# obtain all file names in thread folder
	dir_names = os.listdir(TEMP_THREAD_DIR_PATH)
	
	# obtain file names of all csv files
	thread_files = [j for j in dir_names if ".csv" in j]
		
	# for each thread file
	for thr_file in thread_files:
		
		# load channel data into numpy array
		with open(TEMP_THREAD_DIR_PATH + "/" + thr_file, 'r') as x:
			chan_data_obj = csv.reader(x, delimiter=",")
				
			# add content to array in less efficient way (TEMPORARY SOLUTION UNTILL DATABASE)
			for i, line in enumerate(chan_data_obj):
				
				# if line is the header
				if i == 0:
					
					# extract data
					thr_data = np.array(line)
						
					# extract number of columns for appending data
					num_col = len(thr_data)
																
				# if the line is the right size (likely "," in messages cause errors) and not the header
				elif len(line) == num_col and i != 0:
							
					# store data of line
					thr_data = np.vstack((thr_data, np.array(line)))
		
			
		# if data only contains header
		if len(thr_data.shape) < 2:
						
			# skip this itteration
			continue
			
			
		# # # MAKE SELECTION OF THREAD MESSAGES BASED ON TIME # # #	
		
		# select messages within SEL_RANGE		
		thr_mess_indices = compute_network.select_messages_time(thr_data, SEL_RANGE)
			
			
		# # # MAKE SELECTION OF MESSAGES BASED ON EXCLUDED AUTHORS # # #
		
		# remove messages from accounts in REMOVE_ACCOUNTS
		thr_mess_indices, thr_mess_authors = compute_network.exclude_specific_authors(thr_data, thr_mess_indices, REMOVE_ACCOUNTS)
			
		
		# # # ANALYSIS THREAD CHANNELS DATA   # # #			
		
		# obtain message, interaction and emoji times for thread data
		mess_range, int_range, emoji_range, mess_hourly, int_hourly, emoji_hourly, mess_per_acc, \
			men_per_acc, rep_per_acc, emoji_per_acc, thr_per_acc, int_per_acc = \
			analyse_mess_times(mess_range, int_range, emoji_range, mess_hourly, int_hourly, \
			emoji_hourly, mess_per_acc, men_per_acc, rep_per_acc, emoji_per_acc, thr_per_acc, \
			int_per_acc, thr_data, thr_mess_indices, start_dt, end_dt, last_hourly_hist, \
			acc_names, True, MESS_SUBSTRING, EMOJI_TYPES) 
		
		
	return mess_range, int_range, emoji_range, mess_hourly, int_hourly, emoji_hourly, \
		mess_per_acc, men_per_acc, rep_per_acc, emoji_per_acc, thr_per_acc, int_per_acc, \
		acc_names

# # # # # nested functions # # # # #

def analyse_mess_times(mess_range, int_range, emoji_range, mess_hourly, int_hourly, \
	emoji_hourly, mess_per_acc, men_per_acc, rep_per_acc, emoji_per_acc, thr_per_acc, \
	int_per_acc, data, mess_indices, start_dt, end_dt, last_hourly_hist, \
	acc_names, thr_bool, MESS_SUBSTRING, EMOJI_TYPES):
	"""
	UPDATE
	
	notes:
	int_per_account only reflects partial interactions per account:
	- number of sent replies (not received to your messages)
	- number of sent mentions (not mentioned)
	- number of received emojis (not sent to others)
	- number of sent messages in thread (not received from others in same thread)
	
	mentions in replies or in a thread are not counted as additional 
	interactions. however, they are counted as additional mentions.
	 
	"""
	
	# loop over each message in mess_indices
	for mess_i in mess_indices:
		
		
		# # # CHECK FOR SPECIFIC CONTENT (OPTIONAL) # # #
		
		# extract content of message
		mess_cont = data[mess_i,np.where(data[0,:]=="Content")][0]
		
		# if message contains specified substring (or None are specified)
		if (MESS_SUBSTRING == None) or (any([ss in mess_cont[0] for ss in MESS_SUBSTRING])):
			
			
			# # # ASSESS DATE AND TIME # # #
				
			# set STORE_HOURLY boolean to False
			STORE_HOURLY = False
			
			# extract message creation time
			mess_time = data[mess_i,np.where(data[0,:]=="Created_At")].astype(int)

			# convert to date time format
			mess_date_time = datetime.fromtimestamp(mess_time[0][0]/1000)
			
			# subtract start time of analysis
			date_since_start = mess_date_time - start_dt
			
			
			# # # ASSESS MESSAGE AUTHOR # # #
			
			# extract author of message
			mess_aut = data[mess_i,np.where(data[0,:]=="Author")][0]
					
			# determine index of author in acc_names
			aut_i = np.where(acc_names == mess_aut)[0]
			
			
			# # # COUNT MESSAGE # # #
			
			# add 1 to corresponding day in mess_range
			mess_range[date_since_start.days] += 1
					
			# if message was sent within specified range
			if (mess_date_time >= last_hourly_hist) & (mess_date_time < end_dt):
				
				# set STORE_HOURLY boolean to False
				STORE_HOURLY = True
					
				# store time of message in hourly history		
				mess_hourly[mess_date_time.weekday(), mess_date_time.hour] += 1	
				
				# count for author
				mess_per_acc[aut_i] += 1
				
				
			# if message was sent in thread
			if thr_bool:
				
				# add interaction to corresponding day in int_range
				int_range[date_since_start.days] += 1
					
				# if message was sent within specified range
				if STORE_HOURLY:
					
					# store time of message in hourly history		
					int_hourly[mess_date_time.weekday(), mess_date_time.hour] += 1	
					
					# count for author
					mess_per_acc[aut_i] += 1
					thr_per_acc[aut_i] += 1
					int_per_acc[aut_i] += 1
			
			
			# # # COUNT MENTIONS AND EMOJIS # # #
		
			# if message is default message
			if data[mess_i,np.where(data[0,:]=="Type")] == "DEFAULT":
				
				# count mentions
				_, n_men = compute_network.update_mention_matrix(np.zeros((len(acc_names), len(acc_names))), \
					aut_i, data[mess_i,np.where(data[0,:]=="User_Mentions")], acc_names, True) 
						
				# count emoji reactions
				_, n_react = compute_network.update_react_matrix(np.zeros((len(acc_names), len(acc_names))), \
					aut_i, data[mess_i,np.where(data[0,:]=="Reactions")], acc_names, True, EMOJI_TYPES) 
			
				# if analysis is done for a thread
				if thr_bool:
					
					# update result arrays
					int_range[date_since_start.days] += n_react
					emoji_range[date_since_start.days] += n_react
			
					# if results should also be included in hourly arrays
					if STORE_HOURLY:
					
						# update hourly results arrays
						int_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_react	
						emoji_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_react	
						
						# count for author
						emoji_per_acc[aut_i] += n_react
						int_per_acc[aut_i] += n_react
						men_per_acc[aut_i] += n_men
						
				else:
				
					# update result arrays
					int_range[date_since_start.days] += n_men + n_react
					emoji_range[date_since_start.days] += n_react
			
					# if results should also be included in hourly arrays
					if STORE_HOURLY:
					
						# update hourly results arrays
						int_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_men + n_react	
						emoji_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_react	
						
						# count for author
						emoji_per_acc[aut_i] += n_react
						int_per_acc[aut_i] += n_react + n_men
						men_per_acc[aut_i] += n_men
						
						
			# # # COUNT REPLIES # # #			
						
			# if message is reply
			if data[mess_i,np.where(data[0,:]=="Type")] == "REPLY":
			
				# update reply matrix
				_, n_reply = compute_network.update_reply_matrix(np.zeros((len(acc_names), len(acc_names))), \
					aut_i, data[mess_i,np.where(data[0,:]=="Replied_User")][0][0], acc_names, True) 
			
				# update mention matrix (reply interactor is excluded)
				_, n_men = compute_network.update_mention_matrix(np.zeros((len(acc_names), len(acc_names))), \
					aut_i, data[mess_i,np.where(data[0,:]=="User_Mentions")], acc_names, True, data[mess_i,np.where(data[0,:]=="Replied_User")][0][0]) 
				
				# update emoji reaction matrix
				_, n_react = compute_network.update_react_matrix(np.zeros((len(acc_names), len(acc_names))), \
					aut_i, data[mess_i,np.where(data[0,:]=="Reactions")], acc_names, True, EMOJI_TYPES)
	
				# if analysis is not done for thread
				if thr_bool:
					
					# update result arrays
					int_range[date_since_start.days] += n_react + n_reply
					emoji_range[date_since_start.days] += n_react
			
					# if results should also be included in hourly arrays
					if STORE_HOURLY:
					
						# update hourly results arrays
						int_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_react + n_reply
						emoji_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_react
						
						# count for author
						emoji_per_acc[aut_i] += n_react
						int_per_acc[aut_i] += n_react + n_reply
						men_per_acc[aut_i] += n_men
						rep_per_acc[aut_i] += n_reply
						
				else:
										
					# update result arrays
					int_range[date_since_start.days] += n_men + n_react + n_reply
					emoji_range[date_since_start.days] += n_react
			
					# if results should also be included in hourly arrays
					if STORE_HOURLY:
					
						# update hourly results arrays
						int_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_men + n_react + n_reply
						emoji_hourly[mess_date_time.weekday(), mess_date_time.hour] += n_react	
						
						# count for author
						emoji_per_acc[aut_i] += n_react
						int_per_acc[aut_i] += n_men + n_react + n_reply
						men_per_acc[aut_i] += n_men
						rep_per_acc[aut_i] += n_reply	
	
	return mess_range, int_range, emoji_range, mess_hourly, int_hourly, emoji_hourly, \
		mess_per_acc, men_per_acc, rep_per_acc, emoji_per_acc, thr_per_acc, int_per_acc
