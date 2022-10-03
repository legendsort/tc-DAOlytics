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


def plot_range_metrics(node_clus_range, node_sp_range, node_betw_range, \
	sw_range, edge_dis_range, node_dis_range, node_clus_av,  node_sp_av, \
	node_betw_av, num_edge, num_node, clus_edges, sp_edges, betw_edges, \
		edge_edges, node_edges, in_out_frac, SHOW, SAVE_PATH=None):
	"""
	
	
	
	
	!!!!! UPDATE !!!!!
	
	
	
	
	
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

		
	# initiate figure
	range_met_fig = plt.figure(figsize=(9,10))
		
	# initiate subplot for total graph
	node_deg_ax = range_met_fig.add_subplot(3,2,1)

	# plot node degree data
	plot_range_data(node_dis_range, num_node, node_deg_ax, [node_edges[0],node_edges[-1]], [0.9*np.min(num_node),1.1*np.max(num_node)])
	
	# add title for subplot
	plt.title('Node degree')
 
 
	# initiate subplot for total graph
	edge_weigth_ax = range_met_fig.add_subplot(3,2,2)

	# plot node degree data
	plot_range_data(edge_dis_range, num_edge, edge_weigth_ax, [edge_edges[0],edge_edges[-1]], [0.9*np.min(num_edge),1.1*np.max(num_edge)])
	
	# add title for subplot
	plt.title('Edge weight')
 
 
	# initiate subplot for total graph
	clus_coef_ax = range_met_fig.add_subplot(3,2,3)

	# plot node degree data
	plot_range_data(node_clus_range, node_clus_av, clus_coef_ax, [clus_edges[0],clus_edges[-1]], [0.9*np.min(node_clus_av),1.1*np.max(node_clus_av)]) 
	
	# add title for subplot
	plt.title('Clustering coefficient')
	
	
	# initiate subplot for total graph
	shortest_path_ax = range_met_fig.add_subplot(3,2,4)

	# plot node degree data
	plot_range_data(node_sp_range, node_sp_av, shortest_path_ax, [sp_edges[0],sp_edges[-1]], [0.9*np.min(node_sp_av),1.1*np.max(node_sp_av)])
	
	# add title for subplot
	plt.title('Shortest path')
	
	
	# initiate subplot for total graph
	betw_cent_ax = range_met_fig.add_subplot(3,2,5)

	# plot node degree data
	plot_range_data(node_betw_range, node_betw_av, betw_cent_ax, [betw_edges[0],betw_edges[1]], [0.9*np.min(node_betw_av),1.1*np.max(node_betw_av)])
	
	# add title for subplot
	plt.title('Betweenness centrality')
	
		
	range_met_fig.tight_layout()
	
	# show figure
	if SHOW:
		plt.show()
		
	# save figure
	if SAVE_PATH != None:
		range_met_fig.savefig(SAVE_PATH)
		print("Network metrics time series figure saved in " + SAVE_PATH)
		
	return range_met_fig


# # # # # nested functions # # # # #

def plot_range_data(map_data, line_data, fig_ax, ax1_lim, ax2_lim):
	"""
	"""
	
	# plot colormap on first axis
	fig_ax.imshow(np.flipud(np.transpose(map_data)), interpolation='nearest', \
		cmap="rainbow", extent=[0,len(line_data),ax1_lim[0],ax1_lim[1]], aspect='auto')
	
	# set ylimit for first axis
	fig_ax.set_ylim(ax1_lim)
	
	# add second axis
	betw_av_ax = fig_ax.twinx()
	
	# plot line on second axis
	betw_av_ax.plot(line_data, 'k-', linewidth=2)
	
	# set ylimit for second axis
	betw_av_ax.set_ylim(ax2_lim)
