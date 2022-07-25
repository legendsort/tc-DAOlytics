#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  compute_metrics.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import numpy as np
import networkx as nx


def compute_metrics(graph):
	"""
	Computes network metrics for input graph object 
	
	Input:
	graph - (graph object, 1D np.array, 1d np.array) : (the graph object
		to be analysed, the weighted degree, the fraction of weighted in degree)
		
	Output:
	node_clus - [float] : the clustering coefficient for each node in the
		network (same order as nodes in network)
	node_sp - [float] : the average shortest path length for each node in the
		network (same order as nodes in network)
	node_betw - [float] : the betweenness centrality score for each node 
		in the network (same order as nodes in network)
	sw - float : the small worldness index for the network
	edge_dist - [float] : the weights of all edges in the network
	"""
	
	# # # CLUSTERING COEFFICIENT # # #
	
	# compute clustering coefficient per node
	node_clus_out = nx.clustering(graph)
	node_clus = list(node_clus_out.values())
	
	
	# # # AVERAGE SHORTEST PATH LENGTH # # #
	
	# compute average shortest path length per node
	node_sp_out = dict(nx.all_pairs_shortest_path_length(graph))
	
	# initiate list for average results per node
	node_sp = []
	
	# for each node
	for node in list(node_sp_out.keys()):

		# obtain shortest path lengths to other nodes
		paths = list(node_sp_out[node].values())
		
		# compute mean and store (not include path to self at index 0) 
		node_sp.append(np.mean(np.asarray(paths[1:])))
	
	
	# # # BETWEENNESS # # #
	
	node_betw = list(nx.betweenness_centrality(graph).values())

	
	# # # SMALL WORLDNESS INDEX (Lr/L - C/Cl) # # #
	
	# compute small worldness metric
	sw = nx.omega(graph, seed=1)
		
	
	# # # EDGE WEIGHT DISTRIBUTION # # #
	
	# extract all edge weights
	edge_dist = [graph[s][e]['weight'] for s, e in graph.edges()]
		
	
	return node_clus, node_sp, node_betw, sw, edge_dist

if __name__ == '__main__':
    sys.exit(main(sys.argv))
