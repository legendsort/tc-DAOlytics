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
	
	# # # LARGEST COMPONENT # # #
	
	# determine nodes in largest connected component
	largest_cc = max(nx.connected_components(graph), key=len)
	
	# make subgraph of largest connected component nodes 
	largest_cc_graph = nx.subgraph(graph, largest_cc)
	
	
	# # # CLUSTERING COEFFICIENT # # #
	
	# compute clustering coefficient per node
	node_clus_out = nx.clustering(largest_cc_graph)
	node_clus = list(node_clus_out.values())
	
	
	# # # AVERAGE SHORTEST PATH LENGTH # # #
	
	# compute average shortest path length per node
	node_sp_out = dict(nx.all_pairs_shortest_path_length(largest_cc_graph))
	
	# initiate list for average results per node
	node_sp = []
	
	# for each node
	for node in list(node_sp_out.keys()):

		# obtain shortest path lengths to other nodes
		paths = list(node_sp_out[node].values())
		
		# compute mean and store (not include path to self at index 0) 
		node_sp.append(np.mean(np.asarray(paths[1:])))
	
	
	# # # BETWEENNESS # # #
	
	node_betw = list(nx.betweenness_centrality(largest_cc_graph).values())


	# # # NETWORK CENTRALITY # # #
	
	# compute degree centrality
	deg_cen = nx.degree_centrality(largest_cc_graph)
	
	# compute network level centralization
	net_cen = getCentralization(deg_cen, "degree")
	print("Network centralization = {}".format(net_cen))
	
	
	# # # SMALL WORLDNESS INDEX (Lr/L - C/Cl) # # #
	
	# compute small worldness metric on largest connected component graph
	sw = nx.omega(largest_cc_graph, seed=1)
	#sw = 0
		
	# # # EDGE WEIGHT DISTRIBUTION # # #
	
	# extract all edge weights
	edge_dist = [largest_cc_graph[s][e]['weight'] for s, e in largest_cc_graph.edges()]
		
	
	return node_clus, node_sp, node_betw, sw, edge_dist, largest_cc


# # # # # nested functions # # # # #

def getCentralization(centrality, c_type):
	
	c_denominator = float(1)
	
	n_val = float(len(centrality))
	
	print (str(len(centrality)) + "," +  c_type + "\n")
	
	if (c_type=="degree"):
		c_denominator = (n_val-1)*(n_val-2)
		
	if (c_type=="close"):
		c_top = (n_val-1)*(n_val-2)
		c_bottom = (2*n_val)-3	
		c_denominator = float(c_top/c_bottom)
		
	if (c_type=="between"):
		c_denominator = (n_val*n_val*(n_val-2))
		
	if (c_type=="eigen"):

		'''
		M = nx.to_scipy_sparse_matrix(G, nodelist=G.nodes(),weight='weight',dtype=float)
		eigenvalue, eigenvector = linalg.eigs(M.T, k=1, which='LR') 
		largest = eigenvector.flatten().real
		norm = sp.sign(largest.sum())*sp.linalg.norm(largest)
		centrality = dict(zip(G,map(float,largest)))
		'''
		
		c_denominator = sqrt(2)/2 * (n_val - 2)
		
	#start calculations	
		
	c_node_max = max(centrality.values())


	c_sorted = sorted(centrality.values(),reverse=True)
	
	
	# print ("max node" + str(c_node_max) + "\n")

	c_numerator = 0

	for value in c_sorted:
		
		if c_type == "degree":
			#remove normalisation for each value
			c_numerator += (c_node_max*(n_val-1) - value*(n_val-1))
		else:
			c_numerator += (c_node_max - value)
	
	# print ('numerator:' + str(c_numerator)  + "\n")	
	# print ('denominator:' + str(c_denominator)  + "\n")	

	network_centrality = float(c_numerator/c_denominator)
	
	if c_type == "between":
		network_centrality = network_centrality * 2
		
	return network_centrality
	
	
if __name__ == '__main__':
    sys.exit(main(sys.argv))
