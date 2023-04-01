### Store and Rietrive the network graph from neo4j db

import datetime

# def store_networkx_into_neo4j(networkx_graphs, networkx_dates):
#     """
#     store the networkx graph into neo4j db

#     Parameters:
#     -------------
#     networkx_graphs : list of networkx.classes.graph.Graph or networkx.classes.digraph.DiGraph
#         the list of graph created from user interactions
#     networkx_dates : list of dates
#         the dates for each graph

#     """
#     queries_list = make_graph_list_query(networkx_graphs, networkx_dates)



def make_graph_list_query(networkx_graphs, networkx_dates):
    """
    Make a list of queries for each graph to save their results

    Parameters:
    -------------
    networkx_graphs : list of networkx.classes.graph.Graph or networkx.classes.digraph.DiGraph
        the list of graph created from user interactions
    networkx_dates : list of dates
        the dates for each graph

    Returns:
    ---------
    final_queries : list of str
        list of strings, each is a query for an interaction graph to be created 
    """
    final_queries = []

    for graph, date in zip(networkx_graphs, networkx_dates):
        nodes_dict = graph.nodes.data()
        edges_dict = graph.edges.data()

        query_accounts, query_relations = make_create_network_query(nodes_dict, 
                                            edges_dict,
                                            date)
        ## semi-colon to finish the query
        graph_query = query_accounts + query_relations + ';'


        final_queries.append(graph_query)
    
    return final_queries

def make_create_network_query(nodes_dict, edge_dict, graph_date, nodes_type='DiscordAccount', rel_type='INTERACTED'):
    """
    make string query to save the accounts with their account_name and relationships with their relation from **a graph**
    The query to add the nodes and edges is using `MERGE` operator of Neo4j db since it won't create duplicate nodes and edges if the relation and the account was saved before 

    Parameters:
    -------------
    nodes_dict : NodeDataView
        the nodes of a Networkx graph
    edge_dict : NodeDataView
        the edges of a Networkx graph
    graph_date : datetime
        the date of the interaction in as a python datetime object 
    nodes_type : str
        the type of nodes to be saved
        default is `Account`
    rel_type : str
        the type of relationship to create
        default is `INTERACTED`
    
    Returns:
    ----------
    acc_query : string
        the MERGE query for creating all accounts
    rel_query : string
        the MERGE query for creating all accounts
    """

    iso_date_str = graph_date.isoformat()
    iso_date_now = datetime.datetime.now().isoformat()

    acc_query = ''
    for node in nodes_dict:
        #### retrieving node data
        ## user number
        node_num = node[0]
        ## user account name
        node_acc_name = node[1]['acc_name']
        ## creating the query
        acc_query += f'MERGE (a{node_num}:{nodes_type} {{Username: \'{node_acc_name}\'}})   '
    
    rel_query = ''
    for idx, edge in enumerate(edge_dict):
        #### retrieving edge data

        ## relationship from user number
        starting_acc_num = edge[0]
        ## relationship to user number
        ending_acc_num = edge[1]
        ## the interaction count between them
        interaction_count = edge[2]['weight']

        ## creating the relationship query
        rel_query += f"""MERGE (a{starting_acc_num}) -[rel{idx}:INTERACTED]-> (a{ending_acc_num})"""
        rel_query += f"""ON MATCH 
                            SET 
                                rel{idx}.dates = rel{idx}.dates + ['{iso_date_str}'],
                                rel{idx}.weights = rel{idx}.weights + [{interaction_count}]
                        ON CREATE 
                            SET 
                                rel{idx}.dates = ['{iso_date_str}'],
                                rel{idx}.weights = [{interaction_count}],
                                rel{idx}.createdAt = '{iso_date_now}'

        """
    

    return acc_query, rel_query 