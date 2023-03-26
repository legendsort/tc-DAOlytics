#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  member_activity_history.py
#
#  Author Ene SS Rawa / Tjitse van der Molen


# # # # # import libraries # # # # #

import numpy as np
import networkx as nx
from datetime import datetime
from dateutil.relativedelta import relativedelta

from compute_interaction_matrix_discord import compute_interaction_matrix_discord
from analytics_interactions_script import DB_access
from assess_engagement import assess_engagement


# # # # #

def member_activity_history(db_name, connection_string, channels, acc_names, date_range, window_param, act_param):
    """
    Computes member activity and member interaction network

    Input
    db_name: (str) - guild id
    connection_string: (str) - connection to db string
    channels: [str] - list of all channel ids that should be analysed
    acc_names: [str] - list of all account names that should be analysed
    date_range: [str] - list of first and last date to be analysed (one output per date)
    window_param: [int] -
        entry 1: window size in days. default = 7
        entry 2: step size of sliding window in days. default = 1
        (Currently these values will be default values, in the future, the user might be able to set these in the
        extraction settings page)
    act_param: [int] -
        entry 1: INT_THR - int : minimum number of interactions to be active. Default = 1
        entry 2: UW_DEG_THR - int : minimum number of connections to be active. Default = 1
        entry 3: PAUSED_T_THR - int : time period to remain paused. Default = 1
        entry 4: CON_T_THR - int : time period to assess consistently active. Default = 4
        entry 5: CON_O_THR - int : times to be active within CON_T_THR to be consistently active. Default = 3
        entry 6: EDGE_STR_THR - int : minimum number of interactions for connected. Default = 5
        entry 7: UW_THR_DEG_THR - int : minimum number of accounts for connected. Default = 5
        entry 8: VITAL_T_THR - int : time period to assess for vital. Default = 4
        entry 9: VITAL_O_THR - int : times to be connected within VITAL_T_THR to be vital. Default = 3
        entry 10: STILL_T_THR - int : time period to assess for still active. Default = 3
        entry 11: STILL_O_THR - int : times to be active within STILL_T_THR to be still active. Default = 2
        (Currently these values will be default values, in the future, the user might be able to adjust these)

    Output
    network_dict: {datetime:networkx obj} - dictionary with python datetime objects as keys and networkx graph
        objects as values. The keys reflect the last date of the WINDOW_D day window over which the network was
        computed. The values contain the computed networks.
    activity_dict: {str:{str:set}} - dictionary with keys reflecting each member activity type and dictionaries as
        values. Each nested dictionary contains an index string as key reflecting the number of STEP_D steps have been
        taken since the first analysis period. The values in the nested dictionary are python sets with account names
        that belonged to that category in that period. The length of the set reflects the total number.
    """

    # make empty results output array
    data_out = []

    # # # DATABASE SETTINGS # # #

    # set up database access
    db_access = DB_access(db_name, connection_string)

    # specify the features not to be returned
    ignore_features_db = {'date': 0, 'account_name': 0, 'channel': 0, '_id': 0}


    # # # DEFINE SLIDING WINDOW RANGE # # #

    # determine window start times
    start_dt = datetime.strptime(date_range[0], '%y/%m/%d')
    end_dt = datetime.strptime(date_range[1], '%y/%m/%d')

    time_diff = end_dt - start_dt

    # determine maximum start time (include last day in date_range)
    last_start = time_diff - relativedelta(days = window_param[0]-1)

    # initiate result dictionary for network graphs
    network_dict = {}

    # initiate result dictionaries for engagement types
    all_arrived = {}
    all_consistent = {}
    all_vital = {}
    all_active = {}
    all_connected = {}
    all_new_active = {}
    all_still_active = {}
    all_paused = {}
    all_new_disengaged = {}
    all_disengaged = {}
    all_unpaused = {}
    all_returned = {}

    # # # TO BE IMPLEMENTED: check if there is any past data and if so, load this data instead of creating new dicts


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

        # obtain interaction matrix
        int_mat = compute_interaction_matrix_discord(acc_names, date_list_w_str, channels, db_access)

        # remove interactions with self
        int_mat[np.diag_indices_from(int_mat)] = 0

        # assess engagement
        [graph_out, all_arrived, all_consistent, all_vital, all_active, all_connected, all_paused, all_new_disengaged,
         all_disengaged, all_unpaused, all_returned, all_new_active, all_still_active] = assess_engagement(int_mat,
         w_i, np.asarray(acc_names), act_param, window_param[0], all_arrived, all_consistent, all_vital, all_active,
         all_connected, all_paused, all_new_disengaged, all_disengaged, all_unpaused, all_returned, all_new_active,
         all_still_active)

        # make empty dict for node attributes
        node_att = {}

        # store account names in node_att dict
        for i, node in enumerate(list(graph_out)):
            node_att[node] = acc_names[i]

        # assign account names in node_att to node attributes of graph_out
        nx.set_node_attributes(graph_out, node_att, "acc_name")

        # store results in dictionary
        network_dict[last_date_w] = graph_out


    # # # STORE RESULTS IN FINAL DICTIONARY # # #

    # make empty result dictionary
    activity_dict = {}

    # store results in dictionary
    activity_dict["all_arrived"] = all_arrived
    activity_dict["all_consistent"] = all_consistent
    activity_dict["all_vital"] = all_vital
    activity_dict["all_active"] = all_active
    activity_dict["all_connected"] = all_connected
    activity_dict["all_paused"] = all_paused
    activity_dict["all_new_disengaged"] = all_new_disengaged
    activity_dict["all_disengaged"] = all_disengaged
    activity_dict["all_unpaused"] = all_unpaused
    activity_dict["all_returned"] = all_returned
    activity_dict["all_new_active"] = all_new_active
    activity_dict["all_still_active"] = all_still_active

    return [network_dict, activity_dict]


if __name__ == "__main__":

    ## sample entries
    channels = ["968110585264898048", "1083353697746161774"]
    acc_names = ["danielo#2815", "Ashish G#1920", "katerinabc#6667", "Ene SS Rawa#0855", "sepehr#3795", "mehrdad_mms#8600",
                 "MagicPalm#5706", "Tanusree#3121", "SimonSekavcnik#2162", "Behzad#1761", "DenisFox.#1743", "nimatorabiv#2903"]
    date_range = ['23/02/01', '23/03/01'] # example for longer range of dates (use this for first extraction)
    # date_range = ['23/02/01', '23/02/07']  # example for single day (date range covers exactly window_d days, use this for daily update)

    CONNECTION_STRING = "mongodb://tcmongo:UCk8nV8MuF8v1cM@104.248.137.224:27017/"
    DB_NAME = '915914985140531240'

    ## analysis parameters
    WINDOW_D = 7 # window size in days
    STEP_D = 1 # step size of sliding window in days

    INT_THR = 1  # minimum number of interactions to be active					    Default = 1
    UW_DEG_THR = 1  # minimum number of accounts interacted with to be active	    Default = 1
    PAUSED_T_THR = 1  # time period to remain paused								Default = 1
    CON_T_THR = 4  # time period to be consistent active							Default = 4
    CON_O_THR = 3  # time period to be consistent active							Default = 3
    EDGE_STR_THR = 5  # minimum number of interactions for connected				Default = 5
    UW_THR_DEG_THR = 5  # minimum number of accounts for connected				    Default = 5
    VITAL_T_THR = 4  # time period to assess for vital							    Default = 4
    VITAL_O_THR = 3  # times to be connected within VITAL_T_THR to be vital		    Default = 3
    STILL_T_THR = 3  # time period to assess for still active					    Default = 3
    STILL_O_THR = 2  # times to be active within STILL_T_THR to be still active	    Default = 2

    ## call function
    data_out = member_activity_history(DB_NAME, CONNECTION_STRING, channels, acc_names, date_range, [WINDOW_D, STEP_D],
                                     [INT_THR, UW_DEG_THR, PAUSED_T_THR, CON_T_THR, CON_O_THR, EDGE_STR_THR, UW_THR_DEG_THR,
                                      VITAL_T_THR, VITAL_O_THR, STILL_T_THR, STILL_O_THR])

    print(data_out)