#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_network_metrics.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


def plot_network_metrics(node_clus, node_sp, node_betw, sw, edge_dist, node_dist, in_out_frac, SHOW, SAVE_PATH=None):
	"""
	Plots network metrics
	
	Input:
	node_clus - [float] : the clustering coefficient for each node in the
		network (same order as nodes in graph object)
	node_sp - [float] : the average shortest path length for each node in the
		network (same order as nodes graph object)
	sw - float : the small worldness index for the network
	edge_dist - [float] : the weights of all edges in the network
	node_deg - [float] : the weighted node degree of all nodes in the 
		network (same order as nodes graph object)
	SHOW - bool : whether figure should be shown
	SAVE_PATH = str : path to where figure should be saved, existing figures
		 with same path are overwritten. Set to None to not save figure (default = None)
	"""
	
	# terminate function if output should not be saved or shown
	if SAVE_PATH == None and not SHOW:
		return
		
		
	# # # GENERAL PREPARATIONS # # #
	
	# initiate figure
	net_metrics_fig = plt.figure(figsize=(7,7))
	
	
	# # # EDGE WEIGHT DISTRIBUTION # # #
	
	# initiate subplot for edge distribution
	edge_ax = net_metrics_fig.add_subplot(3,6,(1,3))
	
	plt.hist(edge_dist, 10)
	
	edge_ax.set_xlabel('Edge weight')
	edge_ax.set_ylabel('Number of edges')
	
	
	# # # NODE DEGREE DISTRIBUTION # # #
		
	# initiate subplot for node degree
	deg_ax = net_metrics_fig.add_subplot(3,6,(4,6))
	
	plt.scatter(node_dist, in_out_frac)
	
	deg_ax.set_xlabel('Node degree')
	deg_ax.set_ylabel('(In-Out)/Total')
	
	
	# # # CLUSTERING COEFFICIENT DISTRIBUTION # # #
	
	# initiate subplot for clustering coefficient distribution
	clus_ax = net_metrics_fig.add_subplot(3,6,(7,8))
	
	# plot clustering coefficient distribution and show mean
	clus_ax.violinplot(node_clus, showmeans=True)
	
	# adjust axes
	clus_ax.set_ylabel('Clustering coefficient')
	clus_ax.set_ylim(0, 1)
	clus_ax.set_xticks([])
	
	print("Average clustering coefficient is {}".format(np.mean(np.asarray(node_clus))))
	
	
	# # # AVERAGE SHORTEST PATH LENGTH DISTRIBUTION # # #
	
	# initiate subplot for average shortest path length distribution
	sp_ax = net_metrics_fig.add_subplot(3,6,(9,10))
	
	# plot average shortest path length distribution and show mean
	sp_ax.violinplot(node_sp, showmeans=True)
	
	# adjust axes
	sp_ax.set_ylabel('Average shortest path')
	sp_ax.set_ylim(1, 1.1*max(node_sp))
	sp_ax.set_xticks([])
	
	print("Average shortest path length is {}".format(np.mean(np.asarray(node_sp))))
	
	
	# # # NODE BETWEENNESS CENTRALITY DISTRIBUTION # # #
	
	# initiate subplot for average shortest path length distribution
	betw_ax = net_metrics_fig.add_subplot(3,6,(11,12))
	
	# plot average shortest path length distribution and show mean
	betw_ax.violinplot(node_betw, showmeans=True)
	
	# adjust axes
	betw_ax.set_ylabel('Betweenness centrality')
	betw_ax.set_ylim(0, 1.1*max(node_betw))
	betw_ax.set_xticks([])
	
	print("Average normalized node betweenness centrality is {}".format(np.mean(np.asarray(node_betw))))
	
	
	# # # SMALL WORLDNESS INDEX # # #
	
	# initiate subplot for small worldness index
	sw_ax = net_metrics_fig.add_subplot(3,6,(13,18))
	
	# plot small woldness coefficient value
	sw_ax.scatter(sw, 0, s=30, c="r")
	sw_ax.axvline(x=0, ymin=0.1, ymax=0.9, c="k", dashes=(2,2))
	
	# adjust axes
	sw_ax.set_xlim(-1, 1)
	sw_ax.set_xticks([-1,0,1])
	sw_ax.set_xticklabels(["Lattice like", "Small world", "Random like"])
	sw_ax.set_yticks([])
	
	print("Small worldness coefficient is {}".format(sw))

	
	net_metrics_fig.tight_layout()
	
	
	# show figure
	if SHOW:
		plt.show()
		
	# save figure
	if SAVE_PATH != None:
		net_metrics_fig.savefig(SAVE_PATH)
		print("Network metrics figure saved in " + SAVE_PATH)
		
	return net_metrics_fig

if __name__ == '__main__':
    sys.exit(main(sys.argv))
