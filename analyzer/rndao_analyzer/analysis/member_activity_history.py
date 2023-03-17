#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  member_activity_history.py
#
#  Author Ene SS Rawa / Tjitse van der Molen


# # # # # import libraries # # # # #

import json
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

import db_query


# # # # #

def member_activity_history(db_name, connection_string, channels, acc_names, date_range, window_param, act_param):
    """
    Computes member activity and member interaction network

    :param db_name: (str) - guild id
    :param connection_string: (str) - connection to db string
    :param channels: [str] - list of all channel ids
    :param acc_names: [str] - list of all account names that should be analysed
    :param date_range: [str] - list of first and last date to be analysed (one output per date)
    :param window_param: [int] - first entry: window size in days, second entry: step size of sliding window in days.
        Currently these values will be default values, in the future, the user might be able to set these in the
        extraction settings page
    :param act_param: [int] - first entry: minimal number of interactions for active connections, second entry: minimal
        number of accounts to have at least ac_int_thr interactions with to be active, third entry: minimal number of
        interactions to be connected, fourth entry: minimal number of accounts to have at least con_int_thr interactions
        with to be connected. Currently these values will be default values, in the future, the user might be able to
        set these in the extraction settings page

    :return: [{}] - list with dictionaries containing data per period. The dictionary contains the last date of the
        period and the accounts that belong to the different activity types (active, joined, connected)


    """

    # make empty results output array
    data_out = []

    # # # DATABASE SETTINGS # # #

    # set up database access
    db_access = db_query.DB_access(db_name, connection_string)

    # specify the features not to be returned
    ignore_features_db = {'date': 0, 'account_name': 0, 'channel': 0, '_id': 0}


    # # # DEFINE SLIDING WINDOW RANGE # # #

    # determine window start times
    start_dt = datetime.strptime(date_range[0], '%y/%m/%d')
    end_dt = datetime.strptime(date_range[1], '%y/%m/%d')

    time_diff = end_dt - start_dt

    # determine maximum start time (include last day in date_range)
    last_start = time_diff - relativedelta(days = window_param[0]-1)


    # # # ACTUAL ANALYSIS # # #

    # for every window index
    for w_i in range(int(np.floor(last_start.days / window_param[1]) + 1)):

        # print("window {} of {}".format(w_i + 1, int(np.floor(last_start.days / window_param[1]) + 1)))

        # find last date of window
        last_date_w = start_dt + relativedelta(days=window_param[1] * w_i) + relativedelta(days=window_param[0]-1)

        # make list of all dates in window
        date_list_w = [last_date_w - relativedelta(days=x) for x in range(window_param[0])]

        # make empty array for date string values
        date_list_w_str = np.zeros_like(date_list_w)

        # turn date time values into string
        for i in range(len(date_list_w_str)):
            date_list_w_str[i] = date_list_w[i].strftime('%Y-%m-%d')

        # make empty result array with interactions per account
        int_per_acc = np.zeros(len(acc_names))
        int_above_act_thresh = np.zeros(len(acc_names))
        int_above_con_thresh = np.zeros(len(acc_names))

        # for each account name
        for i, acc in enumerate(acc_names):

            # creating the db query
            int_query = db_query.create_query_sum_interactions([acc], channels, date_list_w_str)

            # initiate cursor for db query
            cursor = db_access.query_db_find(table='heatmaps', query=int_query, ignore_features=ignore_features_db)
            cursor_list = list(cursor)

            # if cursor contains any data
            if len(cursor_list) > 0:

                # extract all interactions from db
                interactions = db_query.sum_interactions_features(cursor_list, cursor_list[0].keys())

                # sum interactions of interest
                all_interactions = interactions["replier"] + interactions["replied"] + interactions["mentioner"] + \
                                   interactions["mentioned"] + interactions["reacter"] + interactions["reacted"] + \
                                   interactions["thr_messages"]

                # store total interactions for account
                int_per_acc[i] = sum(all_interactions)


        # # obtain interaction matrix
        # compute_interaction_matrix_discord(acc_names, date_list_w_str, channels, db_access)
        #
        # # store total accounts that this account has at least act_param[1] interactions with
        # int_above_act_thresh[i] = 0 # # # TODO
        #
        # # store total accounts that this account has at least act_param[3] interactions with # # # TODO
        # int_above_con_thresh[i] = 0  # # # TODO


        # # # STORE ACTIVE ACCOUNTS # # #

        # see which accounts are active
        act_bool = int_per_acc >= act_param[0]
        # act_bool = int_above_act_thresh >= act_param[1]

        # see which accounts are connected
        con_bool = int_above_con_thresh >= act_param[3]


        # # # STORE RESULTS IN FINAL DICTIONARY # # #

        # make empty result dictionary
        activity_dict = {}

        # store results in dictionary
        activity_dict["last_date"] = last_date_w
        activity_dict["active_acc"] = [acc_names[i] for i in range(len(acc_names)) if act_bool[i]] # updated later
        activity_dict["joined_acc"] = [] # added later
        activity_dict["connected_acc"] = [acc_names[i] for i in range(len(acc_names)) if con_bool[i]] # updated later

        data_out.append(activity_dict)

    return data_out




if __name__ == "__main__":

    ## sample entries
    channels = ["👥together-crew", "👥tc-front-end", "👥tc-back-end", "👥tc-design"]
    acc_names = ["danielo#2815", "Ashish G#1920", "katerinabc#6667", "Ene SS Rawa#0855", "sepehr#3795", "mehrdad_mms#8600",
                 "MagicPalm#5706", "Tanusree#3121", "SimonSekavcnik#2162", "Behzad#1761", "DenisFox.#1743", "nimatorabiv#2903"]
    date_range = ['23/02/01', '23/03/01'] # example for longer range of dates (use this for first extraction)
    # date_range = ['23/02/01', '23/02/07']  # example for single day (date range covers exactly window_d days, use this for daily update)

    CONNECTION_STRING = "mongodb://tcmongo:UCk8nV8MuF8v1cM@104.248.137.224:27017/?authMechanism=DEFAULT"
    DB_NAME = '915914985140531240'

    ## analysis parameters
    window_d = 7 # window size in days
    step_d = 1 # step size of sliding window in days

    ac_int_thr = 1 # minimal number of interactions for active connections
    ac_acc_thr = 1 # minimal number of accounts to have at least ac_int_thr interactions with to be active
    con_int_thr = 5 # minimal number of interactions to be connected connection
    con_acc_thr = 5 # minimal number of accounts to have at least con_int_thr interactions with to be connected

    ## call function
    data_out = member_activity_history(DB_NAME, CONNECTION_STRING, channels, acc_names, date_range, [window_d, step_d],
                                     [ac_int_thr, ac_acc_thr, con_int_thr, con_acc_thr])

    print(data_out)