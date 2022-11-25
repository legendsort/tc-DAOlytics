#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  assess_activity_hourly_system_main.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import json
import numpy as np

from assess_activity_hourly_system import assess_activity_hourly_system

# # # # # set groundtruth values # # # # #

GT_NUM_OBJ = 4 # total number of date-channel objects (test 1)
GT_NUM_CH_OBJ = 3 # total number of community health channel date-channel objects (test 2)
GT_CHANNEL_NAME = "community-health" # channel name to run test 2 for
GT_NUM_DATE_OBJ = 2 # total number of 2022-07-02 date-channel objects (test 3)
GT_DATE = "2022-07-02" # date to run test 3 for

GT_ALL_LONE_MESS = [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0] # number of lone messages per hour (test 4)
GT_ALL_THR_MESS = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of thread messages per hour (test 5)
GT_ALL_REP = [0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # number of replies per hour (test 6)
GT_ALL_THR_REP = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of thread replies per hour (test 7)
GT_ALL_MEN = [0,0,0,0,0,0,0,2,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0] # number of mentions per hour (test 8)
GT_ALL_THR_MEN = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of thread mentions per hour (test 9)
GT_ALL_REP_MEN = [0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of reply mentions per hour (test 10)
GT_ALL_EMOJI = [0,0,0,0,0,0,0,3,0,1,0,0,0,0,0,1,0,0,0,0,2,0,0,0] # number of emojis per hour (test 11)

GT_AUT_LONE_MESS = [2,1,0,0,0] # number of lone messages per account (test 12)
GT_AUT_THR_MESS = [0,0,1,0,0] # number of thread messages per account (test 13)
GT_AUT_REP = [0,0,0,1,1] # number of replies per account (test 14)
GT_AUT_THR_REP = [1,0,0,0,0] # number of thread replies per account (test 15)
GT_AUT_MEN = [2,0,0,2,0] # number of mentions per account (test 16)
GT_AUT_THR_MEN = [1,0,0,0,0] # number of thread mentions per account (test 17)
GT_AUT_REP_MEN = [1,0,0,1,1] # number of reply mentions per account (test 18)
GT_AUT_EMOJI = [1,1,1,3,1] # number of emojis per account (test 19)

GT_NUM_MISS_ACC = 1; # number of missing account names provided as input for the function (test 20)
GT_SELF_MEN = 1; # number of times an author mentions themselves (test 21)
GT_SELF_REACT = 1; # number of times an author reacts to their own message (test 22)


# # # # # main function # # # # # 

def main(args):
	
	# specify where test data can be loaded and where output can be saved
	load_name = "./tests/data/test_discord_messages.json"
	save_name = "./tests/data/test_discord_daily_activity.json"
	
	# specify account names
	acc_names = ["danielo#2815", "katerinabc#6667", "WaKa#6616", \
		"Ene SS Rawa#0855"]
			
	# load the test data
	with open(load_name, "rb") as f:
		json_file = json.load(f)

	# run actual function
	error_count = assess_activity_hourly_system(json_file, save_name, acc_names)
			
		
	# load saved output
	with open(save_name, "rb") as f:
		json_out_file = json.load(f)
		
	# make empty result arrays for summed results
	all_lone_messages = np.zeros_like(np.array(json_out_file[0]["lone_messages"]))
	all_thread_messages = np.zeros_like(np.array(json_out_file[0]["thr_messages"]))
	all_replies = np.zeros_like(np.array(json_out_file[0]["replies"]))
	all_thread_replies = np.zeros_like(np.array(json_out_file[0]["thr_replies"]))
	all_mentions = np.zeros_like(np.array(json_out_file[0]["mentions"]))
	all_thread_mentions = np.zeros_like(np.array(json_out_file[0]["thr_mentions"]))
	all_reply_mentions = np.zeros_like(np.array(json_out_file[0]["rep_mentions"]))
	all_emojis = np.zeros_like(np.array(json_out_file[0]["emojis"]))
		
	# set counters for test 2 and 3 to 0
	date_obj_count = 0
	chan_obj_count = 0
		
	# open test_output.txt file
	with open("./tests/test_output.txt", "w") as tf:	
		
		# for each json object
		for json_obj in json_out_file:
			
			# add results to total
			all_lone_messages += np.array(json_obj["lone_messages"])
			all_thread_messages += np.array(json_obj["thr_messages"])
			all_replies += np.array(json_obj["replies"])
			all_thread_replies += np.array(json_obj["thr_replies"])
			all_mentions += np.array(json_obj["mentions"])
			all_thread_mentions += np.array(json_obj["thr_mentions"])
			all_reply_mentions += np.array(json_obj["rep_mentions"])
			all_emojis += np.array(json_obj["emojis"])
			
			# assess date of object
			if json_obj["date"] == GT_DATE:
				date_obj_count += 1
				
			# assess channel of object
			if json_obj["channel"] == GT_CHANNEL_NAME:
				chan_obj_count += 1
		
			# # # print results for object # # #
			print("Date: {}   Channel: {}".format(json_obj["date"], json_obj["channel"]), file=tf)
			
			print("Lone messages: {}".format(np.sum(np.array(json_obj["lone_messages"]),0)), file=tf)		
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["lone_messages"]),1)[i]), file=tf) 
			print("\n", file=tf)
			
			print("Thread messages: {}".format(np.sum(np.array(json_obj["thr_messages"]),0)), file=tf)
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["thr_messages"]),1)[i]), file=tf) 
			print("\n", file=tf)
			
			print("Replies: {}".format(np.sum(np.array(json_obj["replies"]),0)), file=tf)
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["replies"]),1)[i]), file=tf) 
			print("\n", file=tf)
			
			print("Thread replies: {}".format(np.sum(np.array(json_obj["thr_replies"]),0)), file=tf)
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["thr_replies"]),1)[i]), file=tf) 
			print("\n", file=tf)
			
			print("Mentions: {}".format(np.sum(np.array(json_obj["mentions"]),0)), file=tf)
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["mentions"]),1)[i]), file=tf) 
			print("\n", file=tf)
			
			print("Thread mentions: {}".format(np.sum(np.array(json_obj["thr_mentions"]),0)), file=tf)
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["thr_mentions"]),1)[i]), file=tf) 
			print("\n", file=tf)
			
			print("Reply mentions: {}".format(np.sum(np.array(json_obj["rep_mentions"]),0)), file=tf)
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["rep_mentions"]),1)[i]), file=tf) 
			print("\n", file=tf)
			
			print("Emojis: {}".format(np.sum(np.array(json_obj["emojis"]),0)), file=tf)
			for i, name in enumerate(json_obj["acc_names"]):
				print("{}: {}".format(name, np.sum(np.array(json_obj["emojis"]),1)[i]), file=tf) 
			print("\n \n", file=tf)
			
		
		# # # print results summed over all objects # # #
		
		print("All channel-date combinations together", file=tf)
		
		print("Lone messages: {}".format(np.sum(all_lone_messages,0)), file=tf)		
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_lone_messages,1)[i]), file=tf) 
		print("\n", file=tf)
			
		print("Thread messages: {}".format(np.sum(all_thread_messages,0)), file=tf)
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_thread_messages,1)[i]), file=tf) 
		print("\n", file=tf)
			
		print("Replies: {}".format(np.sum(all_replies,0)), file=tf)
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_replies,1)[i]), file=tf) 
		print("\n", file=tf)
			
		print("Thread replies: {}".format(np.sum(all_thread_replies,0)), file=tf)
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_thread_replies,1)[i]), file=tf) 
		print("\n", file=tf)
			
		print("Mentions: {}".format(np.sum(all_mentions,0)), file=tf)
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_mentions,1)[i]), file=tf) 
		print("\n", file=tf)
			
		print("Thread mentions: {}".format(np.sum(all_thread_mentions,0)), file=tf)
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_thread_mentions,1)[i]), file=tf) 
		print("\n", file=tf)
			
		print("Reply mentions: {}".format(np.sum(all_reply_mentions,0)), file=tf)
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_reply_mentions,1)[i]), file=tf) 
		print("\n", file=tf)
			
		print("Emojis: {}".format(np.sum(all_emojis,0)), file=tf)
		for i, name in enumerate(json_out_file[0]["acc_names"]):
			print("{}: {}".format(name, np.sum(all_emojis,1)[i]), file=tf) 
		print("\n", file=tf)
		
		print("Error count: {}".format(error_count), file=tf)
		print("\n", file=tf)
		
		
		# # # print test results # # #
		
		# set all_passed boolean to true
		all_passed = True
		
		# test 1
		if len(json_out_file) == GT_NUM_OBJ:
			print("Test 1: passed", file=tf)
		else:
			print("Test 1: failed", file=tf)
			all_passed = False
		
		# test 2
		if GT_NUM_DATE_OBJ == date_obj_count:
			print("Test 2: passed", file=tf)
		else:
			print("Test 2: failed", file=tf)
			all_passed = False
			
		# test 3
		if GT_NUM_CH_OBJ == chan_obj_count:
			print("Test 3: passed", file=tf)
		else:
			print("Test 3: failed", file=tf)
			all_passed = False
			
		# test 4
		if all(np.sum(all_lone_messages,0) == GT_ALL_LONE_MESS):
			print("Test 4: passed", file=tf)
		else:
			print("Test 4: failed", file=tf)
			all_passed = False
		
		# test 5
		if all(np.sum(all_thread_messages,0) == GT_ALL_THR_MESS):
			print("Test 5: passed", file=tf)
		else:
			print("Test 5: failed", file=tf)
			all_passed = False
			
		# test 6
		if all(np.sum(all_replies,0) == GT_ALL_REP):
			print("Test 6: passed", file=tf)
		else:
			print("Test 6: failed", file=tf)
			all_passed = False
			
		# test 7
		if all(np.sum(all_thread_replies,0) == GT_ALL_THR_REP):
			print("Test 7: passed", file=tf)
		else:
			print("Test 7: failed", file=tf)
			all_passed = False
			
		# test 8
		if all(np.sum(all_mentions,0) == GT_ALL_MEN):
			print("Test 8: passed", file=tf)
		else:
			print("Test 8: failed", file=tf)
			all_passed = False
			
		# test 9
		if all(np.sum(all_thread_mentions,0) == GT_ALL_THR_MEN):
			print("Test 9: passed", file=tf)
		else:
			print("Test 9: failed", file=tf)
			all_passed = False
			
		# test 10
		if all(np.sum(all_reply_mentions,0) == GT_ALL_REP_MEN):
			print("Test 10: passed", file=tf)
		else:
			print("Test 10: failed", file=tf)
			all_passed = False	
			
		# test 11
		if all(np.sum(all_emojis,0) == GT_ALL_EMOJI):
			print("Test 11: passed", file=tf)
		else:
			print("Test 11: failed", file=tf)
			all_passed = False
			
		# test 12
		if all(np.sum(all_lone_messages,1) == GT_AUT_LONE_MESS):
			print("Test 12: passed", file=tf)
		else:
			print("Test 12: failed", file=tf)
			all_passed = False
		
		# test 13
		if all(np.sum(all_thread_messages,1) == GT_AUT_THR_MESS):
			print("Test 13: passed", file=tf)
		else:
			print("Test 13: failed", file=tf)
			all_passed = False
			
		# test 14
		if all(np.sum(all_replies,1) == GT_AUT_REP):
			print("Test 14: passed", file=tf)
		else:
			print("Test 14: failed", file=tf)
			all_passed = False
			
		# test 15
		if all(np.sum(all_thread_replies,1) == GT_AUT_THR_REP):
			print("Test 15: passed", file=tf)
		else:
			print("Test 15: failed", file=tf)
			all_passed = False
			
		# test 16
		if all(np.sum(all_mentions,1) == GT_AUT_MEN):
			print("Test 16: passed", file=tf)
		else:
			print("Test 16: failed", file=tf)
			all_passed = False
			
		# test 17
		if all(np.sum(all_thread_mentions,1) == GT_AUT_THR_MEN):
			print("Test 17: passed", file=tf)
		else:
			print("Test 17: failed", file=tf)
			all_passed = False
			
		# test 18
		if all(np.sum(all_reply_mentions,1) == GT_AUT_REP_MEN):
			print("Test 18: passed", file=tf)
		else:
			print("Test 18: failed", file=tf)
			all_passed = False	
			
		# test 19
		if all(np.sum(all_emojis,1) == GT_AUT_EMOJI):
			print("Test 19: passed", file=tf)
		else:
			print("Test 19: failed", file=tf)
			all_passed = False
			
		# test 20
		if error_count[0] == GT_NUM_MISS_ACC:
			print("Test 20: passed", file=tf)
		else:
			print("Test 20: failed", file=tf)
			all_passed = False
		
		# test 21
		if error_count[2] == GT_SELF_MEN:
			print("Test 21: passed", file=tf)
		else:
			print("Test 21: failed", file=tf)
			all_passed = False
			
		# test 22
		if error_count[3] == GT_SELF_REACT:
			print("Test 22: passed", file=tf)
		else:
			print("Test 22: failed", file=tf)
			all_passed = False
			
			
		print("\n", file=tf)	
		print("All passed: {}".format(all_passed), file=tf)
	
	return
	

	
if __name__ == '__main__':
	sys.exit(main(sys.argv))

