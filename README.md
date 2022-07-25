# DAOlytics

**The current version of the tool can compute and visualize the following measures:**
-	Number of posts, replies, mentions 
-	How often someone is mentioned
-	How often someone mentions other people
-	Heterogeneity in node degree distribution
-	Centrality
-	Indegree
-	Outdegree
-	Betweenness
-	Clustering coefficient
-	Small worldness
-	Heterogeneity in edge weight distribution (not in notion table but in conceptual framework)

**Description of scripts**
Everything can be run and adjusted through the main_graph_analysis_single_time.py script (referred to as main script from here on). The adjustable variables and their meaning are listed below this section.

The main script first calls compute_network.py to compute an interaction network from the raw discord data. Additional outputs are the total number of interactions per node and the fraction of incoming relative to outgoing interactions for each node. 

The main script then calls plot_network.py to create a figure of the total interaction network and the separate networks for each type of interaction (mentions, reactions, replies, thread). The results can be shown and/or saved based on the function input.

The main script then calls compute_network_metrics.py to compute the network metrics for the unweighted and undirected total interaction network. The computed metrics are the clustering coefficient per node. The average shortest path length per node. The normalized betweenness centrality score per node (normalized based on number of nodes in the network). The small worldness index (omega version of computing: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.smallworld.omega.html) for the whole network and the edge weight distribution for the whole network.

Finally, the main script calls plot_network_metrics.py to visualize the clustering coefficient per node and averaged for the whole network. The average shortest path length per node and averaged for the whole network. The normalized betweenness centrality per node and averaged for the whole network. The small worldness index for the whole network. The weighted node degree distribution. The edge weight distribution for the whole network. The results can be shown and/or saved based on the function input. The following network metrics are printed in the terminal: average clustering coefficient, average shortest path length, small worldness index.

**Description adjustable variables**
-	FILENAME = Name of file with discord data (add path if stored in different directory)
-	DIR = Whether directed or undirected networks should be plotted for the network figure
-	SHOW = Whether plotted figures should be shown
-	REMOVE_ACCOUNTS = List of account names that should not be considered in the analysis
-	# TODO MERGE_ACCOUNTS = Account names that should be merged
-	SEL_RANGE = Time range for selecting messages for the analysis
-	EMOJI_TYPES = Emoji's to be considered. (set to None for all emojis)
-	MEN_SUBSTRING = Mentions in messages containing substrings specified in this list are considered only (set to None to consider all messages)
-	REACT_SUBSTRING = Emoji reactions to messages containing substrings specified in this list are considered only (set to None to consider all messages)
-	REPLY_SUBSTRING = Replies containing substrings specified in this list are considered only (set to None to consider all messages)
-	INTERACTION_WEIGHTS = Relative weight of mentions, reactions, replies and threads for constructing the total interaction network
-	NODE_MULT = Node size multiplication for plotting
-	EDGE_MULT = Edge size multiplication for plotting
-	NODE_LEG_VALS = Values to plot for node legend
-	EDGE_LEG_VALS = Values to plot for edge legend
-	NODE_POS_SCALE = Location scale multiplication for plotting

**Notes**
-	All variables in caps can be adjusted by the user in the main script
-	Interactions can be filtered for specific substrings in messages and/or emoji types to make specialized networks like “thank you” networks or voting networks
-	If a person is mentioned in a reply to a message of that same person, the interaction is only counted as reply and not as mention
-	The script only considers accounts that have sent a message or emoji reaction in at least one of the selected channels.
-	Files were converted from xlsx to csv using https://cloudconvert.com/
Data storage
The script currently does not store any intermediate data. The script prints the discord user names that are considered in the analysis in the terminal. The figures do not include the identifying numbers that link the discord account names to the nodes in the network.

