#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  member_activity_history.py
#
#  Author Ene SS Rawa / Tjitse van der Molen


# # # # # import libraries # # # # #

import numpy as np
import networkx as nx
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from compute_interaction_matrix_discord import compute_interaction_matrix_discord
from analytics_interactions_script import DB_access
from assess_engagement import assess_engagement
from member_activity_history_past import check_past_history
from network_graph import make_graph_list_query
from neo4j import GraphDatabase



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

    # initiate result dictionary for network graphs
    network_dict = {}

    # initiate result dictionaries for engagement types
    all_joined = {}
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
    ## TODO: implement the analytics for these 4 variables below
    all_dropped = {}
    all_disengaged_were_newly_active = {}
    all_disengaged_were_consistenly_active = {}
    all_disengaged_were_vital = {}

    # # # checking if there is any past data and if so, load this data instead of creating new dicts

    activity_names_list = ['all_joined', 
                       'all_consistent',
                       'all_vital',
                       'all_active',
                       'all_connected',
                       'all_paused',
                       'all_new_disengaged',
                       'all_disengaged',
                       'all_unpaused',
                       'all_returned',
                       'all_new_active',
                       'all_still_active',
                       'all_dropped',
                       'all_disengaged_were_newly_active',
                       'all_disengaged_were_consistenly_active',
                       'all_disengaged_were_vital'] 
    

    ## past_activities_date is the data from past activities
    ## new_date_range is defined to change the date_range with past data loaded
    ## starting_key is the starting key of actuall analysis 
    past_activities_data, new_date_range, starting_key = check_past_history(db_access=db_access, 
                       date_range=date_range,
                       ## retrive these activities if available
                       activity_names_list=activity_names_list,
                       TABLE_NAME='memberactivities'
                       )

    ## if in past there was an activity, we'll update the dictionaries
    if past_activities_data != {}:
        (all_joined, all_consistent, all_vital, all_active, all_connected,
        all_paused, all_new_disengaged, all_disengaged, all_unpaused,
        all_returned, all_new_active, all_still_active, all_dropped,
        all_disengaged_were_newly_active, all_disengaged_were_consistenly_active,
        all_disengaged_were_vital) = update_activities(past_activities=past_activities_data,
                                                                                activities_list=activity_names_list)
    
    ## if there was still a need to analyze some data in the range
    if new_date_range != []:
        # # # DEFINE SLIDING WINDOW RANGE # # #


        # determine window start times
        start_dt = new_date_range[0]
        end_dt = new_date_range[1]

        time_diff = end_dt - start_dt

        # determine maximum start time (include last day in date_range)
        last_start = time_diff - relativedelta(days = window_param[0]-1)


        # # # ACTUAL ANALYSIS # # #

        # for every window index
        max_range = int(np.floor(last_start.days / window_param[1]) + 1)
        for w_i in range(max_range):
            
            ## update the window index with the data available
            if starting_key != 0:
                ## starting_key plus one should be used since our new data should continue the keys 
                new_window_i = w_i + (starting_key + 1)
            else:
                new_window_i = w_i
            # print("window {} of {}".format(new_window_i + 1, int(np.floor(last_start.days / window_param[1]) + 1)))

            # find last date of window
            last_date_w = start_dt + relativedelta(days=window_param[1] * new_window_i) + relativedelta(days=window_param[0]-1)

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
            (graph_out, all_joined, all_consistent, all_vital, all_active, all_connected, all_paused, all_new_disengaged,
            all_disengaged, all_unpaused, all_returned, all_new_active, all_still_active, all_dropped, 
            all_disengaged_were_vital, all_disengaged_were_newly_active, all_disengaged_were_consistenly_active) = assess_engagement(int_mat,
            new_window_i, np.asarray(acc_names), act_param, window_param[0], all_joined, all_consistent, all_vital, all_active,
            all_connected, all_paused, all_new_disengaged, all_disengaged, all_unpaused, all_returned, all_new_active,
            all_still_active, all_dropped, all_disengaged_were_vital, all_disengaged_were_newly_active, all_disengaged_were_consistenly_active)

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
    activity_dict["all_joined"] = all_joined
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
    activity_dict["all_dropped"] = all_dropped
    activity_dict["all_disengaged_were_vital"] = all_disengaged_were_vital
    activity_dict["all_disengaged_were_newly_active"] = all_disengaged_were_newly_active
    activity_dict["all_disengaged_were_consistenly_active"] = all_disengaged_were_consistenly_active



    
    activity_dict_per_date = store_based_date(start_date=datetime.strptime(date_range[0], '%y/%m/%d'),
                     max_days_after=starting_key + max_range,
                     all_activities=activity_dict)

    return [network_dict, activity_dict_per_date]

def store_based_date(start_date, max_days_after, all_activities):
    """
    store the activities (`all_*`) in a dictionary based on their dates

    Parameters:
    -------------
    start_date : datetime 
        datetime object showing the start date of analysis
    max_days_after : int
        the integer value representing the last date of analysis
    all_activities : dictionary
        the `all_*` activities dictionary
        each key does have an activity, `all_joined`, `all_consistent`, etc
        and values are representing the analytics after the start_date
    """
    ## the data converted to multiple db records
    all_data_records = []

    for day_index in range(max_days_after):
        analytics_date = start_date + timedelta(days=day_index)
        ## saving the data of a record 
        data_record = {}
        data_record['date'] = analytics_date.isoformat()

        ## analytics that were done in that date
        for activity in all_activities.keys():
            ## if an analytics for that day was available
            if str(day_index) in all_activities[activity].keys():
                data_record[activity] = list(all_activities[activity][str(day_index)])
            ## if there was no analytics in that day
            else:
                data_record[activity] = []
        
        # all_data_records[str(day_index)] = data_record
        all_data_records.append(data_record)
    
    return all_data_records

def update_activities(past_activities, activities_list):
    """
    update activities variables using `past_activities` variable
    note: `past_activities` variable contains all the activities from past 
    """
    ## built-in python library
    ## no worries to install it
    from operator import itemgetter

    ## getting all dictionary values with the order of `activities_list`
    activity_dictionaries = itemgetter(*activities_list)(past_activities)
    
    return activity_dictionaries

def store_networkx_into_neo4j(network_dict, driver, dbName):
    """
    store the networkx graph into neo4j db

    Parameters:
    -------------
    networkx_graphs : list of networkx.classes.graph.Graph or networkx.classes.digraph.DiGraph
        the list of graph created from user interactions
    networkx_dates : list of dates
        the dates for each graph
    driver : neo4j._sync.driver.BoltDriver
        the driver to connect to neo4j db
    dbName : str
        the database name to save the results in it
    """
    ## extract the graphs and their corresponding interaction dates
    graph_list, graph_dates = list(network_dict.values()), list(network_dict.keys())

    ## make a list of queries for each date to save the Useraccount and INTERACTED relation between them 
    queries_list = make_graph_list_query(graph_list, graph_dates)

    ## a function to just run the queries inside database session
    identity_function = lambda tx, query: tx.run(query)

    try:
        for query in queries_list:
            with driver.session(database=dbName) as session:
                session.execute_write(
                    identity_function,
                    query=query
                )
    except Exception as e:
        print(f"Error saving the user interactions! exception: {e}")




if __name__ == "__main__":

    ## sample entries
    channels = ["968110585264898048", "1083353697746161774"]
    acc_names = ["danielo#2815", "Ashish G#1920", "katerinabc#6667", "Ene SS Rawa#0855", "sepehr#3795", "mehrdad_mms#8600",
                 "MagicPalm#5706", "Tanusree#3121", "SimonSekavcnik#2162", "Behzad#1761", "DenisFox.#1743", "nimatorabiv#2903"]
    date_range = ['23/02/01', '23/03/01'] # example for longer range of dates (use this for first extraction)
    # date_range = ['23/02/01', '23/02/07']  # example for single day (date range covers exactly window_d days, use this for daily update)

    CONNECTION_STRING = "mongodb://tcmongo:UCk8nV8MuF8v1cM@104.248.137.224:27017/"
    # CONNECTION_STRING = "mongodb://tcmongo:T0g3th3rCr3wM0ng0P55@104.248.137.224:1547/"
    DB_NAME = '915914985140531240'
    # DB_NAME = '1020707129214111824'


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
    data_network_dict, data_activity_dict = member_activity_history(DB_NAME, CONNECTION_STRING, channels, acc_names, date_range, [WINDOW_D, STEP_D],
                                     [INT_THR, UW_DEG_THR, PAUSED_T_THR, CON_T_THR, CON_O_THR, EDGE_STR_THR, UW_THR_DEG_THR,
                                      VITAL_T_THR, VITAL_O_THR, STILL_T_THR, STILL_O_THR])

    print(data_network_dict, data_activity_dict)

    ### saving the newly created dict for network analysis 
    if data_network_dict != {}:
        URI = 'bolt://localhost:7687/neo4j'
        AUTH = ("neo4j", "password")

        with GraphDatabase.driver(URI, auth=AUTH) as driver: 
            driver.verify_connectivity() 

        store_networkx_into_neo4j(data_network_dict, driver, dbName='neo4j')
    