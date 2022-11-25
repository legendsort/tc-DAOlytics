#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  assess_activity_hourly_system.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import json
import numpy as np


# # # # # main function # # # # # 

def assess_activity_hourly_system(json_file, out_file_name, acc_names=[],\
	mess_substring=None, emoji_types=None):
	"""
	Counts activity per hour from json_file and stores in out_file_name
	
	Input:
	json_file - [JSON]: list of JSON objects with message data
	out_file_name - str: path and filename where output is stored
	acc_names - [str]: account names for which activity should be
		counted separately (default = [])
	mess_substring - [str]: only messages containing at least one 
		substring in this list are considered. all messages are 
		considered if set to None (default = None)
	emoji_types - [str]: only emojis in this list are considered. all
		emojis are considered if set to None (default = None)
		
	Output:
	warning_counts - [int]: list of counts for the different possible
		warnings that could be raised by the script:
		1st entry: number of messages sent by author not listed in 
			acc_names
		2nd entry: number of times that a duplicate DayActivity object
			is encounterd. if this happens, the first object in the list
			is used.
		3rd entry: number of times a message author mentions themselves
			in the message. these mentions are not counted
		4rd entry: number of times a message author emoji reacts to
			their own message. these reactions are not counted
			
	Notes:
	The results are saved as JSON objects based on out_file_name
	"""
	
	# initiate array with zeros for counting error occurences
	warning_count = [0]*4
	
	# initiate empty result array for DayActivity objects
	all_day_activity_obj = []
	
	# add remainder category to acc_names
	acc_names.append("remainder")
	
	# for each message
	for mess in json_file:
		
		# # # check for specific message content # # #
		
		# if message contains specified substring (or None are specified)
		if (mess_substring == None) or (any([ss in mess["message_content"] for ss in mess_substring])):
		
			
			# # # extract data # # #
		
			# obtain message date, channel and author
			mess_date = mess["datetime"].split(" ")[0]
			mess_hour = int(mess["datetime"].split(" ")[1].split(":")[0])
			mess_chan = mess["channel"]
			mess_auth = mess["author"]
			
			# obtain index of author in acc_names
			try:
				auth_i = acc_names.index(mess_auth)
			except:
				print("WARNING: author name {} not found in acc_names".format(mess_auth))
				auth_i = -1
				warning_count[0] += 1
		
			# # # obtain object index in object list # # #
		
			# see if an object exists with corresponding date and channel
			all_day_activity_obj, obj_list_i, warning_count = get_obj_list_i(\
				all_day_activity_obj, mess_date, mess_chan, acc_names, warning_count)
		
		
			# # # count # # #
			
			# count reactions				
			n_reac, warning_count = count_reactions(mess["reactions"], \
				emoji_types, mess_auth, warning_count)
			
			# add n_reac to hour of message that received the emoji
			all_day_activity_obj[obj_list_i].emojis[auth_i,mess_hour]+=int(n_reac)
			
			# count mentions
			n_men, n_rep_men, warning_count = count_mentions(mess["user_mentions"], \
				mess["replied_user"], mess_auth, warning_count)
          
			# if message was not sent in thread
			if not mess["thread"]:
				
				# if message is default message
				if mess["mess_type"] == "DEFAULT":	
				
					# add 1 to hour of message
					all_day_activity_obj[obj_list_i].lone_messages[auth_i,mess_hour]+=int(1)
					
					# add n_men to hour of message
					all_day_activity_obj[obj_list_i].mentions[auth_i,mess_hour]+=int(n_men)
					
				
				# if message is reply
				elif mess["mess_type"] == "REPLY":
				
					# add 1 to hour of message
					all_day_activity_obj[obj_list_i].replies[auth_i,mess_hour]+=int(1)
					
					# add n_men to hour of message
					all_day_activity_obj[obj_list_i].mentions[auth_i,mess_hour]+=int(n_men)
					
					# add n_rep_men to hour of message
					all_day_activity_obj[obj_list_i].rep_mentions[auth_i,mess_hour]+=int(n_rep_men)
				
				
			# if message was sent in thread	
			else:
				
				# if message is default message
				if mess["mess_type"] == "DEFAULT":		
				
					# add 1 to hour of message
					all_day_activity_obj[obj_list_i].thr_messages[auth_i,mess_hour]+=int(1)
				
					# add n_men to hour of message
					all_day_activity_obj[obj_list_i].thr_mentions[auth_i,mess_hour]+=int(n_men)
					
					
				# if message is reply	
				elif mess["mess_type"] == "REPLY":
				
					# add 1 to hour of message
					all_day_activity_obj[obj_list_i].thr_replies[auth_i,mess_hour]+=int(1)
					
					# add n_men to hour of message
					all_day_activity_obj[obj_list_i].thr_mentions[auth_i,mess_hour]+=int(n_men)
					
					# add n_rep_men to hour of message
					all_day_activity_obj[obj_list_i].rep_mentions[auth_i,mess_hour]+=int(n_rep_men)
					
											
	# # # store results	# # #
	json_out_file = store_results_json([i.asdict() for i in \
		all_day_activity_obj], out_file_name) 
		
	return warning_count


	
# # # # # classes # # # # #

class DayActivity:
   
	# define constructor
	def __init__(self,date,channel,lone_messages,thr_messages,replies,\
		thr_replies,mentions,thr_mentions,rep_mentions,emojis,acc_names): 
		
		self.date = date
		self.channel = channel
		self.lone_messages = lone_messages
		self.thr_messages = thr_messages
		self.replies = replies
		self.thr_replies = thr_replies
		self.mentions = mentions
		self.thr_mentions = thr_mentions
		self.rep_mentions = rep_mentions
		self.emojis = emojis
		self.acc_names = acc_names
	
	
	# # # functions # # #
	
	# turn object into dictionary	
	def asdict(self):
		return {'date': self.date, 'channel': self.channel, \
			'lone_messages': self.lone_messages.tolist(), 'thr_messages': \
			self.thr_messages.tolist(), 'replies': self.replies.tolist(), \
			'thr_replies': self.thr_replies.tolist(), 'mentions': \
			self.mentions.tolist(), 'thr_mentions': self.thr_mentions.tolist(), \
			'rep_mentions': self.rep_mentions.tolist(), 'emojis': \
			self.emojis.tolist(), 'acc_names': self.acc_names} 
          
          
# # # # # functions # # # # #

def get_obj_list_i(all_day_activity_obj, mess_date, mess_chan, acc_names, warning_count):
	"""
	Assesses index of DayActivity object
	
	Input:
	all_day_activity_obj - [obj]: list of DayActivity objects
	mess_date - str: date in which message was sent yyyy-mm-dd
	mess_chan - str: name of channel in which message was sent
	num_rows - int: number of rows for count arrays in DayActivity
	
	Output:
	all_day_activity_obj - [obj]: updated list of DayActivity objects
	obj_list_i - int: index of DayActivity object in 
		all_day_activity_obj that corresponds to the message
		
	Notes:
	if no corresponding DayActivity object is found in 
	all_day_activity_obj, a new DayActivity object is appended
	"""
	
	# check if DayActivity object corresponding to mess_date and mess_chan exists	
	obj_overlap = [all([getattr(obj,'date','Attribute does not exist')==mess_date, \
		getattr(obj,'channel','Attribute does not exist')==mess_chan]) \
		for obj in all_day_activity_obj]
			
	# if there is no object for the channel date combination
	if not any(obj_overlap):
			
		# create DayActivity object and add it to the list
		all_day_activity_obj.append(DayActivity(mess_date, mess_chan, \
			np.zeros((len(acc_names),24), dtype=np.int16), np.zeros((len(acc_names),24), dtype=np.int16), \
			np.zeros((len(acc_names),24), dtype=np.int16), np.zeros((len(acc_names),24), dtype=np.int16), \
			np.zeros((len(acc_names),24), dtype=np.int16), np.zeros((len(acc_names),24), dtype=np.int16), \
			np.zeros((len(acc_names),24), dtype=np.int16), np.zeros((len(acc_names),24), dtype=np.int16), \
			acc_names))
			
		# set list index for message
		obj_list_i = int(-1)
			
	else:
			
		# set list index for message
		obj_list_i = int(obj_overlap.index(True))
			
		# see if object only occurs once and raise error if more than once
		if sum(obj_overlap) > 1:
			print("WARNING: duplicate DayActivity object, first entry in list is used")
			warning_count[1] += 1
			
	return all_day_activity_obj, obj_list_i, warning_count

# # #

def count_mentions(mess_mentions, replied_user, mess_auth, warning_count):
	"""
	Counts number of user mentions in a message
	
	Input:
	mess_mentions - [str]: all user account names that are mentioned in 
		the message
	replied_user - str: account name of author who is replied to if
		message type is reply
	mess_auth - str: message author
	
	Output:
	n_men - int: number of mentions in message
	n_rep_men - int: number of times the author of the message that is 
		replied to is mentioned in the message
	
	Notes:
	authors mentioning themselves are not counted
	"""
	
	# set number of interactions to 0
	n_men = 0
	n_rep_men = 0
          
	# for each interaction
	for mentioned in mess_mentions:
				
		# if mentioned account is the same as message author
		if mentioned == mess_auth: 
					
			# print error and skip
			print("WARNING: {} mentioned themselves. This is not counted".format(mess_auth))
			warning_count[2] += 1
					
		else:
					
			# if mentioned account is not the account that was replied to
			if mentioned != replied_user: 
						
				# add 1 to number of mentions
				n_men += 1
						
			else:
				
				# add 1 to number of replied mentions
				n_rep_men += 1
				
	return n_men, n_rep_men, warning_count
		
# # #

def count_reactions(mess_reactions, emoji_types, mess_auth, warning_count):
	"""
	Counts number of reactions to a message
	
	Input:
	mess_reactions - [[str]]: list with a list for each emoji type, 
		containing the accounts that reacted with this emoji and the
		emoji type (last entry of lists within list)
	emoji_types - [str] or None: list of emoji types to be considered.
		All emojis are considered when None
	mess_auth - str: message author
	
	Output:
	n_reac - int: number of emoji reactions to post
	
	notes:
	emojis reacted by the author of the message are not counted
	"""
						
	# set number of reactions to 0
	n_reac = 0
			
	for emoji_type in mess_reactions:
						
		# if reacting account is in acc_names and reacted emoji is part of emoji_types if defined
		if (emoji_types == None) or (emoji_type[-1] in emoji_types):
					
			# for each account that reacted with this emoji		
			for reactor in emoji_type[:-1]:
								
				# if the message author posted the emoji
				if reactor == mess_auth:
								
					# print error and skip
					print("WARNING: {} reacted to themselves. This is not counted".format(mess_auth))
					warning_count[3] += 1
				
				# if the reactor is not empty	
				elif len(reactor)>0:
							
					# add 1 to number of reactions
					n_reac += 1	
	
	return n_reac, warning_count
	
# # #

def store_results_json(save_dict, file_name, print_out=False):
	"""
	Stores dictionary or list of dictionaries as JSON file
	
	Input:
	save_dict - {}, [{}]: dictionary or list of dictionaries to be saved
	file_name - str: name (including path) to where data is saved
	print_out - bool: whether message should be printed confirming that
		the data is saved
		
	Output:
	out_file - JSON: JSON file with content from save_dict
	
	Notes:
	JSON file is also saved in location specified by file_name
	"""
	
	# initiate output file
	with open(file_name, "w") as f:
		
		# store results
		json.dump(save_dict, f)
	
	# # save and close output file
	# out_file.close()
	
	if print_out:
		print("data saved at: " + file_name)

