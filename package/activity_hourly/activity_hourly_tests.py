#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  activity_hourly_tests.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import json
import numpy as np

from activity_hourly import activity_hourly

# # # # # set groundtruth values # # # # #

GT_NUM_OBJ = 4 # total number of date-channel objects (test 1)
GT_NUM_CH_OBJ = 3 # total number of community health channel date-channel objects (test 2)
GT_CHANNEL_NAME = "community-health" # channel name to run test 2 for
GT_NUM_DATE_OBJ = 2 # total number of 2022-07-02 date-channel objects (test 3)
GT_DATE = "2022-07-02" # date to run test 3 for

# ground truth data for tests on single channel-day combination defined by GT_CHANNEL_NAME and GT_DATE
GT_ALL_LONE_MESS = [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0] # number of lone messages per hour (test 4)
GT_ALL_THR_MESS = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of thread messages per hour (test 5)
GT_ALL_REPLIER = [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of replies sent per hour (test 6)
GT_ALL_REPLIED = [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of replies received per hour (test 7)
GT_ALL_MENTIONER = [0,0,0,0,0,0,0,2,1,0,0,0,0,0,0,0,0,1,0,0,2,0,0,0] # number of mentions sent per hour (test 8)
GT_ALL_MENTIONED = [0,0,0,0,0,0,0,2,1,0,0,0,0,0,0,0,0,1,0,0,2,0,0,0] # number of mentions received per hour (test 9)
GT_ALL_REP_MENTIONER = [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of reply mentions sent per hour (test 10)
GT_ALL_REP_MENTIONED = [0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0] # number of reply mentions received per hour (test 11)
GT_ALL_REACTER = [0,0,0,0,0,0,0,3,1,1,0,0,0,0,0,1,0,0,0,0,2,0,0,0] # number of emojis sent per hour (test 12)
GT_ALL_REACTED = [0,0,0,0,0,0,0,3,1,1,0,0,0,0,0,1,0,0,0,0,2,0,0,0] # number of emojis received per hour (test 13)

GT_AUT_LONE_MESS = [1,1,0,0,1] # number of lone messages per account (test 14)
GT_AUT_THR_MESS = [0,0,1,0,0] # number of thread messages per account (test 15)
GT_AUT_REPLIER = [2,0,0,1,1] # number of replies per account (test 16)
GT_AUT_REPLIED = [1,0,2,0,1] # number of replies per account (test 17)
GT_AUT_MENTIONER = [4,0,0,2,0] # number of mentions per account (test 18)
GT_AUT_MENTIONED = [1,3,1,0,1] # number of mentions per account (test 19)
GT_AUT_REP_MENTIONER = [2,0,0,1,1] # number of reply mentions per account (test 20)
GT_AUT_REP_MENTIONED = [1,0,2,0,1] # number of reply mentions per account (test 21)
GT_AUT_REACTER = [5,2,0,0,1] # number of emojis per account (test 22)
GT_AUT_REACTED= [2,1,1,3,1] # number of emojis per account (test 23)

GT_NUM_MISS_ACC = 2 # number of messages from authors not inclued in acc_names (test 24)
GT_SELF_MEN = 1 # number of times an author mentions themselves (test 25)
GT_SELF_REACT = 1 # number of times an author reacts to their own message (test 26)
GT_NUM_MISS_EMOJI = 1 # number of emojis from senders not included in acc_names (test 27)
GT_NUM_MISS_MEN = 2 # number of mentions of accounts not included in acc_names (both direct mentions and reply mentions) (test 28)
GT_NUM_MISS_REP = 1 # number of replies to accounts not included in acc_names (test 29)

			
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
	warning_count = activity_hourly(json_file, save_name, acc_names)
			
		
	# load saved output
	with open(save_name, "rb") as f:
		json_out_file = json.load(f)
		
	# make empty result arrays for summed results
	all_lone_messages = np.zeros_like(np.array(json_out_file[0]["lone_messages"]))
	all_thread_messages = np.zeros_like(np.array(json_out_file[0]["thr_messages"]))
	all_replier = np.zeros_like(np.array(json_out_file[0]["replier"]))
	all_replied = np.zeros_like(np.array(json_out_file[0]["replied"]))
	all_mentioner = np.zeros_like(np.array(json_out_file[0]["mentioner"]))
	all_mentioned = np.zeros_like(np.array(json_out_file[0]["mentioned"]))
	all_rep_mentioner = np.zeros_like(np.array(json_out_file[0]["rep_mentioner"]))
	all_rep_mentioned = np.zeros_like(np.array(json_out_file[0]["rep_mentioned"]))
	all_reacter = np.zeros_like(np.array(json_out_file[0]["reacter"]))
	all_reacted = np.zeros_like(np.array(json_out_file[0]["reacted"]))
	
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
			all_replier += np.array(json_obj["replier"])
			all_replied += np.array(json_obj["replied"])
			all_mentioner += np.array(json_obj["mentioner"])
			all_mentioned += np.array(json_obj["mentioned"])
			all_rep_mentioner += np.array(json_obj["rep_mentioner"])
			all_rep_mentioned += np.array(json_obj["rep_mentioned"])
			all_reacter += np.array(json_obj["reacter"])
			all_reacted += np.array(json_obj["reacted"])
			
			# assess date of object
			if json_obj["date"][0] == GT_DATE:
				date_obj_count += 1
				
			# assess channel of object
			if json_obj["channel"][0] == GT_CHANNEL_NAME:
				chan_obj_count += 1
		
			# # # print results for object # # #
			print("Date: {}   Channel: {}".format(json_obj["date"], json_obj["channel"]), file=tf)
			
						
			print_channel_date_combination("Lone messages", np.array(json_obj["lone_messages"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Thread messages", np.array(json_obj["thr_messages"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Replier", np.array(json_obj["replier"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Replied", np.array(json_obj["replied"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Mentioner", np.array(json_obj["mentioner"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Mentioned", np.array(json_obj["mentioned"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Reply mentioner", np.array(json_obj["rep_mentioner"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Reply mentioned", np.array(json_obj["rep_mentioned"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Reacter", np.array(json_obj["reacter"]), json_obj["acc_names"], tf)
			print_channel_date_combination("Reacted", np.array(json_obj["reacted"]), json_obj["acc_names"], tf)
			
		
		# # # print results summed over all objects # # #
		
		print("All channel-date combinations together", file=tf)
		
		print_channel_date_combination("Lone messages", all_lone_messages, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Thread messages", all_thread_messages, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Replier", all_replier, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Replied", all_replied, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Mentioner", all_mentioner, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Mentioned", all_mentioned, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Reply mentioner", all_rep_mentioner, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Reply mentioned", all_rep_mentioned, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Reacter", all_reacter, json_out_file[0]["acc_names"], tf)
		print_channel_date_combination("Reacted", all_reacted, json_out_file[0]["acc_names"], tf)

			
		# # # print warning counts # # #
		
		print("Error count: {}".format(warning_count), file=tf)
		print("\n", file=tf)
		
		
		# # # print test results # # #
		
		# set all_passed boolean to true
		all_passed = [None] * 29

		# check test outcome and print results
		all_passed[0] = assess_test(len(json_out_file) == GT_NUM_OBJ, 1, tf)
		all_passed[1] = assess_test(GT_NUM_DATE_OBJ == date_obj_count, 2, tf)
		all_passed[2] = assess_test(GT_NUM_CH_OBJ == chan_obj_count, 3, tf)
		all_passed[3] = assess_test(all(np.sum(all_lone_messages,0) == GT_ALL_LONE_MESS), 4, tf)
		all_passed[4] = assess_test(all(np.sum(all_thread_messages,0) == GT_ALL_THR_MESS), 5, tf)
		all_passed[5] = assess_test(all(np.sum(all_replier,0) == GT_ALL_REPLIER), 6, tf)
		all_passed[6] = assess_test(all(np.sum(all_replied,0) == GT_ALL_REPLIED), 7, tf)
		all_passed[7] = assess_test(all(np.sum(all_mentioner,0) == GT_ALL_MENTIONER), 8, tf)
		all_passed[8] = assess_test(all(np.sum(all_mentioned,0) == GT_ALL_MENTIONED), 9, tf)
		all_passed[9] = assess_test(all(np.sum(all_rep_mentioner,0) == GT_ALL_REP_MENTIONER), 10, tf)
		all_passed[10] = assess_test(all(np.sum(all_rep_mentioned,0) == GT_ALL_REP_MENTIONED), 11, tf)
		all_passed[11] = assess_test(all(np.sum(all_reacter,0) == GT_ALL_REACTER), 12, tf)
		all_passed[12] = assess_test(all(np.sum(all_reacted,0) == GT_ALL_REACTED), 13, tf)
		all_passed[13] = assess_test(all(np.sum(all_lone_messages,1) == GT_AUT_LONE_MESS), 14, tf)
		all_passed[14] = assess_test(all(np.sum(all_thread_messages,1) == GT_AUT_THR_MESS), 15, tf)
		all_passed[15] = assess_test(all(np.sum(all_replier,1) == GT_AUT_REPLIER), 16, tf)
		all_passed[16] = assess_test(all(np.sum(all_replied,1) == GT_AUT_REPLIED), 17, tf)
		all_passed[17] = assess_test(all(np.sum(all_mentioner,1) == GT_AUT_MENTIONER), 18, tf)
		all_passed[18] = assess_test(all(np.sum(all_mentioned,1) == GT_AUT_MENTIONED), 19, tf)
		all_passed[19] = assess_test(all(np.sum(all_rep_mentioner,1) == GT_AUT_REP_MENTIONER), 20, tf)
		all_passed[20] = assess_test(all(np.sum(all_rep_mentioned,1) == GT_AUT_REP_MENTIONED), 21, tf)
		all_passed[21] = assess_test(all(np.sum(all_reacter,1) == GT_AUT_REACTER), 22, tf)
		all_passed[22] = assess_test(all(np.sum(all_reacted,1) == GT_AUT_REACTED), 23, tf)
		all_passed[23] = assess_test(warning_count[0] == GT_NUM_MISS_ACC, 24, tf)
		all_passed[24] = assess_test(warning_count[2] == GT_SELF_MEN, 25, tf)
		all_passed[25] = assess_test(warning_count[3] == GT_SELF_REACT, 26, tf)
		all_passed[26] = assess_test(warning_count[4] == GT_NUM_MISS_EMOJI, 27, tf)
		all_passed[27] = assess_test(warning_count[5] == GT_NUM_MISS_MEN, 28, tf)
		all_passed[28] = assess_test(warning_count[6] == GT_NUM_MISS_REP, 29, tf)
			
		# assess whether all tests passed and print results
		print("\n", file=tf)	
		print("All passed: {}".format(all(all_passed)), file=tf)
	
	return
	
	
def print_channel_date_combination(count_type, count_data, acc_names, file_handle):
	"""
	Prints total counts and counts per account into file
	
	Input:
	count_type - str: interaction/message type that is counted
	count_data - [[int]]: np 2D array with counts per hour per account
	acc_names - [str]: all account names in count_data
	file_handle - handle: handle referencing file where output should be
		printed
		
	Output:
	Printed results in output file
	"""
	
	# print sum over all accounts
	print(count_type + ": {}".format(np.sum(count_data,0)), file=file_handle)
	
	# for each account name in acc_names		
	for i, name in enumerate(acc_names):
		# print count for account
		print("{}: {}".format(name, np.sum(count_data,1)[i]), file=file_handle) 
	
	# print empty line
	print("\n", file=file_handle)

# # #

def assess_test(test_out, test_num, file_handle):
	"""
	Assess if test passed and prints results in output file
	
	Input:
	test_out - bool: outcome of test
	test_num - int: test number
	file_handle - handle: handle referencing file where output should be
		printed
		
	Output:
	test_out - bool: outcome of test
	Printed results in output file
	"""
		
	# if the test passed
	if test_out:
		# print that test passed
		print("Test {}: passed".format(test_num), file=file_handle)
		
	else:
		# print that test failed
		print("Test {}: failed".format(test_num), file=file_handle)

	return test_out
			
	
if __name__ == '__main__':
	sys.exit(main(sys.argv))

