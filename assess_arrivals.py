#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  assess_arrivals.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import os
import csv
import shutil
import numpy as np
from datetime import datetime


def assess_arrivals(arr_data, SEL_RANGE):
	"""
	Assess number of new members based on arrival data
	
	Input:
	arr_data - np array : loaded contents of arrival csv file(s)
	SEL_RANGE - [str,str] : list of two strings indicating start and 
		end time to include in analysis ('yy/mm/dd HH:MM:SS')
		
	Output:
	num_arr_period - float : number of accounts that arrived in the 
		specified period
	arrived_list - [str] : list of account names that have arrived in
		server in specified period
	"""
	
	# # # MAKE SELECTION OF MESSAGES BASED ON TIME # # #
	
	mess_indices = select_messages_time(arr_data, SEL_RANGE)
	
	
	# # # ASSESS NEW ARRIVALS IN TIME RANGE # # #
	
	# create empty result list
	arrived_list = []
	
	# loop over each message from main channels
	for mess_i in mess_indices:
		
		# if message is member join message
		if arr_data[mess_i,np.where(arr_data[0,:]=="Type")] == "GUILD_MEMBER_JOIN":
			
			# obtain account name of member that joins
			arrived_list.append(arr_data[mess_i, np.where(arr_data[0,:]=="Author")][0][0])
			
			
	return len(arrived_list), arrived_list


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
	mess_times = data[1:,np.where(data[0,:]=="Created_At")].astype(int)
	
	# convert selection range dates to time
	sel_start = datetime.strptime(SEL_RANGE[0], '%y/%m/%d %H:%M:%S')
	sel_end = datetime.strptime(SEL_RANGE[1], '%y/%m/%d %H:%M:%S')
	
	# make empty result array
	mess_indices = np.asarray([])
	
	# for each message time
	for i,t in enumerate(mess_times):
		
		# convert to date time format and add to list
		mess_date_time = datetime.fromtimestamp(t[0][0]/1000)
		
		# if message was sent within specified range
		if (mess_date_time >= sel_start) & (mess_date_time < sel_end):
			
			# store index of message for analysis
			mess_indices = np.append(mess_indices, i+1)
	
	# change to integer array
	mess_indices = mess_indices.astype('int')
	
	return mess_indices
	
