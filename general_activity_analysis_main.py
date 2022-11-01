#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  general_activity_analysis_main.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import os
import shutil
import numpy as np
from datetime import datetime
import time
import json

import matplotlib.pyplot as plt
import seaborn as sns

from load_data import load_csv_data
from compute_community_activity import compute_community_activity

# # # # # set parameter values # # # # #

DATA_DIR_PATH = "./data/aragon220919/" # path to directory with server data
CHANNELS = ["ambassadorchat", "anttoken", "bugsfeedback", "communitygeneral", "communitywellbeing", "daoexpertsgenerl", "daopolls", "data", \
	"design", "devspace", "dgov", "espanol", \
	"finance", "general", "governancegeneral", "growthsquad", \
	"kudos", "learninglibrary", "legal", "meetups", \
	"memespets", "newjoiners", "operationsgeneral", \
	"questions", "spamreporting", "support", \
	"tweetsnews"] # names of channels to be used for analysis (should correspond to directories in DATA_DIR_PATH)   

TEMP_THREAD_DIR_PATH = "./temp_thread" # path to temporary directory where thread data from all channels will be combined

DAY_HIST = 28 # number of days into the past to consider with hourly activity (ideally multiple of 7)
MIN_MESS = 1 # minimal number of messages to be considered active
MOV_WIND = 7 # number of days in sliding window for range

REMOVE_ACCOUNTS = ["Aragon🦅 Blog#0000", "Aragon🦅 Twitter#0000"] # list of account names that should not be considered in the analysis
MERGE_ACCOUNTS = []#[("thegadget.eth#3374", "sepehr#3795")] # list of tuples with account names that should be merged (only first name in tuple remains)
SEL_RANGE = ['22/04/01 00:00:00', '22/09/18 00:00:00'] # range of dates and times to include in analysis ('yy/mm/dd HH:MM:SS')

EMOJI_TYPES = None # emoji's to be considered. (set to None for all emojis)   # thank you: ["❤", "💜", "💜", "🙏", "❤️", "🙌"]   
MESS_SUBSTRING = None # messages containing substrings specified in this list are considered only (set to None for all messages)

SHOW = [True, True, True] # whether plotted figures should be shown


# # # # # main function # # # # # 

def main(args):

	# set start time of script
	startTime = time.time()
	
	# # # INITIATE RESULT ARRAYS # # #
	
	# compute duration of total range
	time_diff = datetime.strptime(SEL_RANGE[1], '%y/%m/%d %H:%M:%S') - datetime.strptime(SEL_RANGE[0], '%y/%m/%d %H:%M:%S')
	range_duration = time_diff.days
		
	# make empty result arrays
	mess_chan = np.zeros((len(CHANNELS)))
	aut_chan = np.zeros((len(CHANNELS)))
	men_chan = np.zeros((len(CHANNELS)))
	rep_chan = np.zeros((len(CHANNELS)))
	emoji_chan = np.zeros((len(CHANNELS)))
	thr_chan = np.zeros((len(CHANNELS)))
	int_chan = np.zeros((len(CHANNELS)))
		
	mess_range = np.zeros((range_duration))
	int_range = np.zeros((range_duration))
	emoji_range = np.zeros((range_duration))
		
	mess_hourly = np.zeros((7,24))
	int_hourly = np.zeros((7,24))
	emoji_hourly = np.zeros((7,24))
		
		
	# # # FOR EACH CHANNEL # # #

	for i, chan in enumerate(CHANNELS):
			
				
		# # # LOAD AND PREPARE CHANNEL DATA # # #
		
		# remove temporary directory for thread data if it exists
		if os.path.exists(TEMP_THREAD_DIR_PATH):
			shutil.rmtree(TEMP_THREAD_DIR_PATH)
			
		# make temporary directory for all thread data
		os.mkdir(TEMP_THREAD_DIR_PATH)
			
		# load all data from specified channels into one data file
		data = load_csv_data([chan], DATA_DIR_PATH, TEMP_THREAD_DIR_PATH)
						
						
		# # # ANALYSE ACTIVITY # # #	
		
		mess_range_chan, int_range_chan, emoji_range_chan, mess_hourly_chan, \
			int_hourly_chan, emoji_hourly_chan, mess_per_acc_chan, men_per_acc_chan, \
			rep_per_acc_chan, emoji_per_acc_chan, thr_per_acc_chan, int_per_acc_chan, acc_names_chan = \
			compute_community_activity(data, REMOVE_ACCOUNTS, MERGE_ACCOUNTS, \
			SEL_RANGE, EMOJI_TYPES, MESS_SUBSTRING, DAY_HIST, TEMP_THREAD_DIR_PATH)


		# # # STORE RESULTS # # #
		
		mess_range += mess_range_chan
		int_range += int_range_chan
		emoji_range += emoji_range_chan
		
		mess_hourly += mess_hourly_chan
		int_hourly += int_hourly_chan
		emoji_hourly += emoji_hourly_chan
			
		mess_chan[i] = np.sum(mess_per_acc_chan)
		aut_chan[i] = np.sum(mess_per_acc_chan >= MIN_MESS)
		men_chan[i] = np.sum(men_per_acc_chan)
		rep_chan[i] = np.sum(rep_per_acc_chan)
		emoji_chan[i] = np.sum(emoji_per_acc_chan)
		thr_chan[i] = np.sum(thr_per_acc_chan)
		int_chan[i]	= np.sum(int_per_acc_chan)
		
	
	# obtain analysis time of script
	analysisTime = (time.time() - startTime)
	print('Analysis time in seconds: ' + str(analysisTime))
	
	
	# # # DEFINE FILE IDENTIFIER # # #
		
	# make file identifier based on parameter selection
	file_identifier = "community_activity_analysis_aragon_220401_220918_{}dayHist.json".format(DAY_HIST)
	
	
	# # # SAVE RESULTS # # #
	
	# prepare result dictionaries
	
	range_dict = {"messages" : mess_range.tolist(), "interactions" : \
		int_range.tolist(), "emojis" : emoji_range.tolist()}
	hourly_dict = {"messages" : mess_hourly.tolist(), "interactions" : \
		int_hourly.tolist(), "emojis" : emoji_hourly.tolist()}
	channel_dict = {"channels" : CHANNELS, "messages" : mess_chan.tolist(), \
		"authors" : aut_chan.tolist(), "mentions" : men_chan.tolist(), "replies" : \
		rep_chan.tolist(), "emojis" : emoji_chan.tolist(), "threads" : thr_chan.tolist(), \
		"interactions" : int_chan.tolist()}
	
	# prepare file names
	
	range_file_name = "./json/range_" + file_identifier
	hourly_file_name = "./json/hourly_" + file_identifier
	channel_file_name = "./json/channel_" + file_identifier
	
	# save results
	
	store_results_json(range_dict, range_file_name)
	store_results_json(hourly_dict, hourly_file_name)
	store_results_json(channel_dict, channel_file_name)
	
	# obtain save time of script
	saveTime = (time.time() - analysisTime)
	print('Save time in seconds: ' + str(saveTime))
	
	print(np.sum(mess_range))
	print(np.sum(emoji_range))
	print(np.sum(int_range))
	
	
	# # # PLOT CHANNELS FIGURE # # #
	
	if SHOW[0]:
			
		# sort channels based on num messages
		sort_i = np.argsort(mess_chan, axis=None)
			
		
		# initiate figure for channel comparison results
		comp_fig = plt.figure(figsize=(16,5))
		
		# initiate subplot for messages
		mess_ax = comp_fig.add_subplot(1,7,1)
		
		# plot results
		plt.barh(range(mess_chan.shape[0]), mess_chan[sort_i]) 
		
		# add title
		mess_ax.title.set_text('Messages')
		
		# add ytick labels
		plt.yticks(ticks=range(mess_chan.shape[0]), labels=np.asarray(CHANNELS)[sort_i])
		
		
		# initiate subplot for authors
		aut_ax = comp_fig.add_subplot(1,7,2)
		
		# plot results
		plt.barh(range(mess_chan.shape[0]), aut_chan[sort_i]) 
		
		# add title
		aut_ax.title.set_text('Authors')
		
		# remove ytick labels
		plt.yticks(ticks=[])
		
		
		# initiate subplot for mentions
		men_ax = comp_fig.add_subplot(1,7,3)
		
		# plot results
		plt.barh(range(men_chan.shape[0]), men_chan[sort_i]) 
		
		# add title
		men_ax.title.set_text('Mentions')
		
		# remove ytick labels
		plt.yticks(ticks=[])
		
		
		# initiate subplot for replies
		rep_ax = comp_fig.add_subplot(1,7,4)
		
		# plot results
		plt.barh(range(rep_chan.shape[0]), rep_chan[sort_i]) 
		
		# add title
		rep_ax.title.set_text('Replies')
		
		# remove ytick labels
		plt.yticks(ticks=[])
		
		
		# initiate subplot for emojis
		rep_ax = comp_fig.add_subplot(1,7,5)
		
		# plot results
		plt.barh(range(emoji_chan.shape[0]), emoji_chan[sort_i]) 
		
		# add title
		rep_ax.title.set_text('Emoji reactions')
		
		# remove ytick labels
		plt.yticks(ticks=[])
		
		
		# initiate subplot for threads
		thr_ax = comp_fig.add_subplot(1,7,6)
		
		# plot results
		plt.barh(range(thr_chan.shape[0]), thr_chan[sort_i]) 
		
		# add title
		thr_ax.title.set_text('Thread messages')
		
		# remove ytick labels
		plt.yticks(ticks=[])
		
		
		# initiate subplot for threads
		int_ax = comp_fig.add_subplot(1,7,7)
		
		# plot results
		plt.barh(range(int_chan.shape[0]), int_chan[sort_i]) 
		
		# add title
		int_ax.title.set_text('Interactions')
		
		# remove ytick labels
		plt.yticks(ticks=[])
		
			
		comp_fig.tight_layout()
		plt.show()
		
		
	# # # RANGE FIGURE # # #
	
	if SHOW[1]:
	
		# initiate figure for range data
		range_fig = plt.figure(figsize=(8,6))
		
		# initiate subplot for messages
		rec_ax = range_fig.add_subplot(3,1,1) 
		
		# compute moving average
		mess_mov_av = np.convolve(mess_range, np.ones((MOV_WIND))/MOV_WIND, 'valid')		
		
		# plot results
		plt.plot(range(len(mess_range)), mess_range, color='#CFCFCF', linewidth=1)
		plt.plot(range(int(np.floor(MOV_WIND)/2), len(mess_range)-int(np.floor(MOV_WIND)/2)), mess_mov_av, color='#33a02c', linewidth=2)
		
		
		# add axis lables
		plt.ylabel("# Messages per day")
		
		# # add xtick labels
		# plt.xticks(ticks = date_tick_i, labels = date_tick_labels)
		
		# adjust axes
		plt.xlim(0,len(mess_range)-1)
		
		
		# initiate subplot for interactions
		rec_ax = range_fig.add_subplot(3,1,2)  
		
		# compute moving average
		int_mov_av = np.convolve(int_range, np.ones((MOV_WIND))/MOV_WIND, 'valid')	
		
		# plot results
		plt.plot(range(len(int_range)), int_range, color='#CFCFCF', linewidth=1)
		plt.plot(range(int(np.floor(MOV_WIND)/2), len(int_range)-int(np.floor(MOV_WIND)/2)), int_mov_av, color='#1f78b4', linewidth=2)
		
		
		# add axis lables
		plt.ylabel("# Interactions per day")
		
		# # add xtick labels
		# plt.xticks(ticks = date_tick_i, labels = date_tick_labels)
		
		# adjust axes
		plt.xlim(0,len(int_range)-1)
		
		
		# initiate subplot for emojis
		rec_ax = range_fig.add_subplot(3,1,3)  
		
		# compute moving average
		emoji_mov_av = np.convolve(emoji_range, np.ones((MOV_WIND))/MOV_WIND, 'valid')	
		
		# plot results
		plt.plot(range(len(emoji_range)), emoji_range, color='#CFCFCF', linewidth=1)
		plt.plot(range(int(np.floor(MOV_WIND)/2), len(emoji_range)-int(np.floor(MOV_WIND)/2)), emoji_mov_av, color='#C85200', linewidth=2)
		
		
		# add axis lables
		plt.ylabel("# Emojis per day")
		
		# # add xtick labels
		# plt.xticks(ticks = date_tick_i, labels = date_tick_labels)
		
		# adjust axes
		plt.xlim(0,len(emoji_range)-1)
			
		range_fig.tight_layout()
		plt.show()
		
	
	# # # HOURLY FIGURE # # #
	
	if SHOW[2]:
		
		# initiate figure for hourly data
		hourly_fig = plt.figure(figsize=(8,4))	
			
		# specify x and y tick labels
		x_tick_labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", \
			"12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
		y_tick_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
			
		# make heatmap of results	
		hm_ax = sns.heatmap(int_hourly, cmap="Greens", linewidth=1, annot=True, \
			xticklabels=x_tick_labels, yticklabels=y_tick_labels, cbar=False, fmt='.0f')
		
		# add title
		plt.title('Last {} days'.format(DAY_HIST))
		
		# move xtick label to above figure
		hm_ax.xaxis.tick_top()
		
		# rotate tick labels
		plt.xticks(rotation=0) 
		plt.yticks(rotation=0)
		
		
		hourly_fig.tight_layout()
		plt.show()	
		
		
		
	# # # REMOVE TEMPORARY DIRECTORY WITH THREAD DATA # # #
	shutil.rmtree(TEMP_THREAD_DIR_PATH)


# # # # # OTHER FUNCTIONS # # # # #

def store_results_json(save_dict, file_name, print_out=True):
	
	# initiate output file
	out_file = open(file_name, "w")
	
	# store results
	json.dump(save_dict, out_file)
	
	# save output file
	out_file.close()
	
	if print_out:
		print("data saved at: " + file_name)
		
if __name__ == '__main__':
	sys.exit(main(sys.argv))

