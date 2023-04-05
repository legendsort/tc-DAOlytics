#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  network_functions.py
#
#  Author Ene SS Rawa / Tjitse van der Molen


# # # # # import libraries # # # # #
import networkx as nx
import numpy as np
from datetime import datetime, timedelta

from analytics_interactions_script import (sum_interactions_features, per_account_interactions)
from analytics_interactions_script import Query
from db_connection import DB_access

# # # # # functions # # # # #

def discord_interact_analysis_main(guild, db_path, acc_names, last_date, day_range, channel_selection):
    """

    """

    # # # CONNECT TO DB # # #

    # set up database access
    db_access = DB_access(guild, db_path)


    # # # SELECT DATES # # #

    # make empty result array for analysis dates
    analysis_dates = []

    # for each number of dates within day_range
    for day in range(day_range):

        # set date
        day_date = last_date - timedelta(days=day)

        # store date as string
        analysis_dates.append(day_date.strftime("%Y-%m-%d"))


    # # # MAKE NETWORK # # #

    # run function to compute interaction matrix
    int_mat_out = compute_interaction_matrix_discord(acc_names, analysis_dates, channel_selection, db_access)

    # run function to turn interaction matrix into graph
    graph_out = make_graph(int_mat_out)


    # # # LARGEST COMPONENT AND SIZE CHECK # # #

    # run function to extract largest component of graph
    lc_out = extract_lc(graph_out)

    # if network has less than 4 nodes
    if len(lc_out) < 4:

        # return None for the metrics
        print("ERROR: largest component contains only {} nodes".format(len(lc_out)))
        return


    # # # NODE METRICS # # #

    # compute clustering per node
    node_clus = compute_clustering(lc_out)

    # compute average shortest path length per node
    node_av_sp = compute_av_shortest_paths(lc_out)

    # compute betweenness per node
    node_betw = compute_betweenness(lc_out)

    # compute degree centrality per node
    node_deg_cen = compute_degree_centrality(lc_out)

    # compute number of incoming interactions per node
    int_in = np.sum(int_mat_out, 0, dtype=int)

    # compute number of outgoing interactions per node
    int_out = np.sum(int_mat_out, 1, dtype=int)


    # # # HEALTH METRICS # # #

    # compute cohesion score
    coh_score = np.nanmean(node_clus)*200

    # compute decentralization score
    dec_score = 2 * (100 - (compute_centralization(node_deg_cen, "degree") * 100))

    # compute small worldness score
    # sw_score = 100 - (compute_sw_score(lc_out) * 100)
    sw_score = None


    return {"acc_names":acc_names, "network_graph":graph_out, "cohesion_score":coh_score, "decentralization_score":
        dec_score, "small_world_score":sw_score, "node_clus":node_clus, "node_av_sp":node_av_sp, "node_betw":node_betw,
        "int_in":int_in, "int_out":int_out}



def compute_interaction_matrix_discord(acc_names, dates, channels, db_access):
    """
    Computes interaction network from discord data
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

            # if the interacting account in in acc_names
            if int_acc["account"] in acc_names:

                # store data in int_network
                int_mat[np.where(np.array(acc_names) == acc)[0][0], np.where(np.array(acc_names) ==
                                                                             int_acc["account"])[0][0]] = int_acc["count"]

    return int_mat

# # #

def make_graph(mat):
    """
    Turns interaction matrix into graph object

    Input:
    mat - np.array : interaction matrix

    Output:
    graph - graph object: interaction graph
    """

    # make empty result matrix (for undirected matrix)
    new_mat = np.zeros_like(mat)

    # for each row
    for r in range(np.shape(mat)[0]):

        # for each column
        for c in range(r):

            # sum (r,c) and (c,r) values and store
            new_mat[r, c] = mat[r, c] + mat[c, r]

    # turn matrix into graph
    graph = nx.from_numpy_array(new_mat)

    return graph

# # #

def extract_lc(graph):
    """
    extracts largest component of network graph

    Input:
    graph - networkx graph object: the graph for which the largest component should be returned

    Output:
    largest_cc_graph = networkx graph object: the largest component of graph
    """

    # determine nodes in largest connected component
    largest_cc = max(nx.connected_components(graph), key=len)

    # make subgraph of largest connected component nodes
    largest_cc_graph = nx.subgraph(graph, largest_cc)

    return largest_cc_graph

# # #

def compute_clustering(graph):
    """
    Computes clustering coefficient per node for graph

    Input:
    graph - networkx graph object: the graph for which the clustering coefficient should be computed

    Output:
    node_clus_list = [float]: clustering coefficient per node
    """

    # compute clustering coefficient per node
    node_clus_out = nx.clustering(graph)

    # turn results into list
    node_clus_list = np.asarray(list(node_clus_out.values()))

    return node_clus_list

# # #

def compute_av_shortest_paths(graph):
    """
    Computes average shortest path length per node for graph

    Input:
    graph - networkx graph object: the graph for which the average shortest path lengths should be computed

    Output:
    node_av_sp_list = [float]: average shortest path length per node
    """

    # compute average shortest path length per node
    node_sp_out = dict(nx.all_pairs_shortest_path_length(graph))

    # initiate list for average results per node
    node_av_sp_list = []

    # for each node
    for node in list(node_sp_out.keys()):

        # obtain shortest path lengths to other nodes
        paths = list(node_sp_out[node].values())

        # compute mean and store (not include path to self at index 0)
        node_av_sp_list.append(np.mean(np.asarray(paths[1:])))

    return node_av_sp_list

# # #

def compute_betweenness(graph):
    """
    Computes betweenness score per node for graph

    Input:
    graph - networkx graph object: the graph for which the average shortest path lengths should be computed

    Output:
    node_betw_list = [float]: betweenness per node
    """

    # compute node betweenness
    node_betw_list = list(nx.betweenness_centrality(graph).values())

    return node_betw_list

# # #

def compute_degree_centrality(graph):
    """
    Computes degree centrality score per node for graph

    Input:
    graph - networkx graph object: the graph for which the average shortest path lengths should be computed

    Output:
    deg_cen_list = [float]: degree centrality per node
    """

    # compute degree centrality
    deg_cen_list = list(nx.degree_centrality(graph).values())

    return deg_cen_list

# # #

def compute_sw_score(graph):
    """
    Computes small worldness score (omega method) graph

    Input:
    graph - networkx graph object: the graph for which the small worldness score should be computed

    Output:
    sw_score = float: small worldness score
    """

    # compute sw score with omega method
    sw_score = nx.omega(graph, seed=1)

    return sw_score

# # #

def extract_edge_dist(graph):
    """
    Extracts all edge weights of a graph

    Input:
    graph - networkx graph object: the graph for which the edge weight distribution should be extracted

    Output:
    sw_score = float: small worldness score
    """

    # extract all edge weights
    edge_weights = [largest_cc_graph[s][e]['weight'] for s, e in largest_cc_graph.edges()]

    return edge_weights

# # #

def compute_centralization(centrality, c_type):
    """
    Computes centralization score of a graph

    Input:
    centrality - [float]]: list of centrality scores per node
    c_type - str: type of centrality that should be computed ("degree" , "close", "between", "eigen")

    Output:
    network_centrality = float: centrality score
    """
    c_denominator = float(1)

    n_val = float(len(centrality))

    if (c_type == "degree"):
        c_denominator = (n_val - 1) * (n_val - 2)

    if (c_type == "close"):
        c_top = (n_val - 1) * (n_val - 2)
        c_bottom = (2 * n_val) - 3
        c_denominator = float(c_top / c_bottom)

    if (c_type == "between"):
        c_denominator = (n_val * n_val * (n_val - 2))

    if (c_type == "eigen"):
        '''
        M = nx.to_scipy_sparse_matrix(G, nodelist=G.nodes(),weight='weight',dtype=float)
        eigenvalue, eigenvector = linalg.eigs(M.T, k=1, which='LR') 
        largest = eigenvector.flatten().real
        norm = sp.sign(largest.sum())*sp.linalg.norm(largest)
        centrality = dict(zip(G,map(float,largest)))
        '''

        c_denominator = sqrt(2) / 2 * (n_val - 2)

    # start calculations

    c_node_max = max(centrality)

    c_sorted = sorted(centrality, reverse=True)

    # print ("max node" + str(c_node_max) + "\n")

    c_numerator = 0

    for value in c_sorted:

        if c_type == "degree":
            # remove normalisation for each value
            c_numerator += (c_node_max * (n_val - 1) - value * (n_val - 1))
        else:
            c_numerator += (c_node_max - value)

    # print ('numerator:' + str(c_numerator)  + "\n")
    # print ('denominator:' + str(c_denominator)  + "\n")

    network_centrality = float(c_numerator / c_denominator)

    if c_type == "between":
        network_centrality = network_centrality * 2

    return network_centrality