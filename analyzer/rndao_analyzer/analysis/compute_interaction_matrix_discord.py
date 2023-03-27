#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compute_interaction_matrix_discord.py
#
#  Author Ene SS Rawa / Tjitse van der Molen

# # # # # import libraries # # # # #
import numpy as np
from datetime import datetime, timedelta

from analysis.analytics_interactions_script import (DB_access, Query, sum_interactions_features, per_account_interactions)

def compute_interaction_matrix_discord(acc_names, dates, channels, db_access):
    """
    Computes interaction matrix from discord data

    Input:
    acc_names - [str] : list of all account names to be considered for analysis
    dates - [str] : list of all dates to be considered for analysis
    channels - [str] : list of all channel ids to be considered for analysis
    db_access - obj : database access object
    
    Output:
    
    """

    feature_projection = {
        'thr_messages': 0,
        'lone_messages': 0,
        'replier': 0,
        'replied': 0,
        'mentioner': 0,
        'mentioned': 0,
        'reacter': 0,
        'reacted': 0,
        '__v': 0
    }

    # make empty result array
    int_mat = np.zeros((len(acc_names), len(acc_names)))

    # for each acc_name
    for acc in acc_names:

        # intiate query
        query = Query()

        # set up query dictionary
        query_dict = query.create_query_filter_account_channel_dates(
            acc_names=[acc],
            channels=channels,
            dates=dates,
            date_key='date',
            channel_key='channelId',
            account_key='account_name'
        )

        # create cursor for db
        cursor = db_access.query_db_find(table='heatmaps',
                                         query=query_dict,
                                         feature_projection=feature_projection)

        # get results from db
        db_results = per_account_interactions(cursor_list=list(cursor), dict_keys=['replied_per_acc', 'reacted_per_acc' , 'mentioner_per_acc'])

        # obtain results for all interactions summed together
        acc_out_int = db_results["all_interaction_accounts"]

        # for each interacting account
        for int_acc in acc_out_int.values():

            # if the interacting account is in acc_names
            if int_acc["account"] in acc_names:

                # store data in int_network
                int_mat[np.where(np.array(acc_names) == acc)[0][0], np.where(np.array(acc_names) ==
                                                                             int_acc["account"])[0][0]] = int_acc["count"]

    return int_mat
