#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  plot_network.py
#  
#  Author Ene SS Rawa / Tjitse van der Molen  
 

# # # # # import libraries # # # # #

import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# # # # # main function # # # # #

def plot_network_num_interactions(total_graph, men_graph, react_graph, reply_graph, \
	thread_graph, acc_names, DIR, SHOW, NODE_MULT=10, EDGE_MULT=0.25, NODE_LEG_VALS=[10,50,100], \
	EDGE_LEG_VALS=[1,10,30], NODE_POS_SCALE=10, SAVE_PATH=None):
	"""
	Plots summed network and separate individual networks as figure 
	
	Input:
	for each type of network (total, mention, react, reply, thread): 
	graph, sum, in_frac - (graph, 1D np.array, 1d np.array) : (the graph
		object, weighted degree, fraction of weighted in degree)
	acc_names - [str] : all active accounts
	DIR - bool : whether a directed network was constructed
	SHOW - bool : whether figure should be shown
	NODE_MULT - float/int : node size multiplication for plotting (default = 10)	
	EDGE_MULT - float/int : edge width multiplication for plotting (default = 0.25)
	NODE_LEG_VALS = [float/int] : values to plot for node legend (default = [10, 50, 100])
	EDGE_LEG_VALS = [float/int] : values to plot for edge legend (default = [1, 10, 30])
	NODE_POS_SCALE = int : node location scale multiplication for plotting (default = 10)
	SAVE_PATH = str : path to where figure should be saved, existing figures
		 with same path are overwritten. Set to None to not save figure (default = None)
	
	Notes:
	Shows number of interactions and fraction of incoming vs outgoing
		interactions on nodes if DIR = True in main script
	"""
	
	# terminate function if output should not be saved or shown
	if SAVE_PATH == None and not SHOW:
		return
			
				
	# # # GENERAL PREPARATIONS # # #
	
	# compute node positions
	node_positions = nx.kamada_kawai_layout(total_graph[0], scale=NODE_POS_SCALE)
	
	# obtain maximum edge value
	max_edge = int(max([EDGE_LEG_VALS[-1], max([total_graph[0][s][e]['weight'] for s, e in total_graph[0].edges()])]))
	
	# initiate figure
	net_fig = plt.figure(figsize=(14,6))
	
	
	# # # TOTAL GRAPH # # #
	
	# initiate subplot for total graph
	total_ax = net_fig.add_subplot(1,2,1)
	
	# plot network for total_graph
	plot_graph(total_graph, NODE_MULT, EDGE_MULT, node_positions, max_edge)
	
	# add title
	plt.title("All interactions")
	
	# adjust axes
	plt.axis('off')
	x_ax_lim = total_ax.get_xlim()
	y_ax_lim = total_ax.get_ylim()
	total_ax.set_xlim([1.1*x for x in x_ax_lim])
	total_ax.set_ylim([1.1*y for y in y_ax_lim])
	
	
	# # # LEGEND # # #
	
	# add invisible circles for node legend
	node_leg_entries = []
	for n in NODE_LEG_VALS:
		node_leg_entry = plt.scatter([], [], s=n*NODE_MULT, c="w", edgecolors="k")
		node_leg_entries.append(node_leg_entry)
	
	# add invisible lines for edge legend
	edge_color_range = plt.cm.Greys(np.linspace(-max_edge, max_edge, 2*max_edge+1))
	edge_leg_entries = []
	for e in EDGE_LEG_VALS:
		edge_leg_entry = Line2D([],[], linewidth=e*EDGE_MULT, color=edge_color_range[max_edge+e])
		edge_leg_entries.append(edge_leg_entry)
		
	# add node legend
	node_leg = plt.legend(handles=node_leg_entries, labels=NODE_LEG_VALS, labelspacing=2, loc='upper left', bbox_to_anchor=(1, 0.5), frameon=False, title="Total")
	
	# add edge legend
	edge_leg = plt.legend(handles=edge_leg_entries, labels=EDGE_LEG_VALS, labelspacing=2, loc='lower left', bbox_to_anchor=(1, 0.5), frameon=False, title="Pairwise")
	
	# include first added legend so that both are shown
	plt.gca().add_artist(node_leg)
	
	if DIR:
		# add colorbar
		sm = plt.cm.ScalarMappable(cmap=plt.get_cmap("seismic"), norm=plt.Normalize(vmin=-1, vmax=1))
		sm._A = []
		plt.colorbar(sm, location="bottom", fraction=0.05, pad=0.01, ticks=[-1,0,1], label="(In-Out)/Total")
	
	
	# # # MENTION GRAPH # # #
	
	# initiate subplot for mention graph
	men_ax = net_fig.add_subplot(2,4,3)
	
	# plot network for mentions graph
	plot_graph(men_graph, NODE_MULT, EDGE_MULT, node_positions, max_edge)
	
	# add title
	plt.title("Mentions")

	
	
	# # # REACTION GRAPH # # #
	
	# initiate subplot for reaction graph
	react_ax = net_fig.add_subplot(2,4,4)
		
	# plot network for reactions graph
	plot_graph(react_graph, NODE_MULT, EDGE_MULT, node_positions, max_edge)
	
	# add title
	plt.title("Emoji reactions")
	
	
	# # # REPLY GRAPH # # #
	
	# initiate subplot for reply graph
	reply_ax = net_fig.add_subplot(2,4,7)
	
	# plot network for reply graph
	plot_graph(reply_graph, NODE_MULT, EDGE_MULT, node_positions, max_edge)
	
	# add title
	plt.title("Direct replies")


	# # # THREAD GRAPH # # #
	
	# initiate subplot for thread graph
	thread_ax = net_fig.add_subplot(2,4,8)
	
	# TODO plot network for thread graph
	plt.axis('off')
	
	# add title
	plt.title("Threads")
	

	net_fig.tight_layout()
	
	# show figure
	if SHOW:
		plt.show()
		
	# save figure
	if SAVE_PATH != None:
		net_fig.savefig(SAVE_PATH)
		print("Network figure saved in " + SAVE_PATH)
	
	return
	
	
# # # # # nested functions # # # # #

def plot_graph(graph_info, node_mult, edge_mult, node_positions, edge_max):	
	"""
	Makes plot of a graph object
	
	Input:
	graph_info - (graph, 1D np.array, 1d np.array) : (graph object, 
		weighted degree, fraction of weighted in degree)
	node_mult - float/int : node size multiplication for plotting
	edge_mult - float/int : edge width multiplication for plotting
	node_positions = networkX pos object : locations where to plot each node in the graph
	edge_max = [float/int] : maximum edge value
	
	Output:
	Plots graph in current axis
		
	"""

	# unpack graph info content
	graph = graph_info[0]
	n_sizes = graph_info[1]
	in_frac = graph_info[2]
	
	# select nodes that should be plotted
	node_selection = np.where(n_sizes>0)[0].tolist()
	
	# make subgraph based on node selection
	sub_graph = graph.subgraph(node_selection)
	
	# Get weights from sub_graph
	weights = np.asarray([sub_graph[s][e]['weight'] for s, e in sub_graph.edges()])
	
	# plot subgraph
	nx.draw_networkx(sub_graph, pos=node_positions, arrows=False, with_labels=False, \
		node_size=n_sizes[node_selection]*node_mult, node_color=in_frac[node_selection], \
		cmap=plt.get_cmap("seismic"), vmin=-1, vmax=1, width=weights*edge_mult, edge_color=weights, \
		edge_cmap=plt.get_cmap("Greys"), edge_vmin=-edge_max, edge_vmax=edge_max, edgecolors="k")

	# adjust axes
	plt.axis('off')
	axis = plt.gca()
	x_ax_lim = axis.get_xlim()
	y_ax_lim = axis.get_ylim()
	axis.set_xlim([1.1*x for x in x_ax_lim])
	axis.set_ylim([1.1*y for y in y_ax_lim])
