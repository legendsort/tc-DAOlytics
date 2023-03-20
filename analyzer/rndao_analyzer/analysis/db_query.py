from pymongo import MongoClient
#from pprint import pprint
from numpy import zeros

class DB_access:

   def __init__(self, db_name, connection_string) -> None:
      self.db_client = self._get_database(db_name, connection_string)

   def _get_database(self, db_name, connection_string):
      """
      get the database instance

      Parameters:
      ------------
      db_name : string
         the name of the database to use
      connection_string : string
         the url of connection

      Returns:
      ---------
      client : MongoClient
         the mongodb client to access
      """
      client = MongoClient(connection_string)
      return client[db_name]
   

   def query_db_aggregation(self, query, table, ignore_features=None):
      """
      aggregate the database using query

      Parameters:
      ------------
      table : string
         the table name to retrieve the data
      query : dictionary
         the query as a dictionary
      ignore_features : dictionary
         the dictionary to not to project the results on it
         default is None, meaning to return all features

      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query 
      """
      if ignore_features is None:
         cursor = self.db_client[table].aggregate(query)
      else:
         cursor = self.db_client[table].find(query)

      return cursor
  
   def query_db_find(self, table, query, ignore_features=None):
      """
      aggregate the database using query

      Parameters:
      ------------
      table : string
         the table name to retrieve the data
      query : dictionary
         the query as a dictionary
      ignore_features : dictionary
         the dictionary to not to project the results on it
         default is None, meaning to return all features

      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query 
      """
      if ignore_features is None:
         cursor = self.db_client[table].find(query)
      else:
         cursor = self.db_client[table].find(query, ignore_features)

      return cursor


def create_query_sum_interactions(acc_names, channels, dates, variable_aggregation_type='and', value_aggregation_type='or'):
   """
   etrieves data from several accounts, channels and/or days from the database
   and sums the counts per hour over all retrieved data

   
   Parameters:
   -------------
   acc_names : list of string
      each string is an account name that needs to be included. 
      The minimum length of this list is 1
   channels : list of string
      each string is a channel identifier for the channels that need to be included. 
      The minimum length of this list is 1
   dates : list of datetime
       each datetime object is a date that needs to be included. 
       The minimum length of this list is 1
       should be in type of `%Y-%m-%d` which is the exact database format
   variable_aggregation_type : string
      values can be [`and`, `or`], the aggregation type between the variables (variables are `acc_names`, `channels`, and `dates`)
      `or` represents the or between the queries of acc_name, channels, dates
      `and` represents the and between the queries of acc_name, channels, dates
      default value is `and`
   value_aggregation_type : string
      values can be [`and`, `or`], the aggregation type between the values of each variable
      `or` represents the `or` operation between the values of input arrays
      `and` represents the `and` operation between the values of input arrays
      default value is `or`

   Returns:
   ----------
   query : dictionary
      the query to get access
   """

   #### checking the length of arrays ####
   if len(acc_names) < 1:
      raise ValueError(f"acc_names array is empty!")
   if len(channels) < 1:
      raise ValueError(f"channels array is empty!")
   if len(dates) < 1:
      raise ValueError(f"dates array is empty!")
   
   ## checking the variable aggregation_type variable
   if variable_aggregation_type not in ['and', 'or']:
      raise ValueError(f'variable aggregation type must be either `and` or `or`!\nentered value is:{variable_aggregation_type}')
   
   ## checking the value aggregation_type variable
   if value_aggregation_type not in ['and', 'or']:
      raise ValueError(f'value aggregation type must be either `and` or `or`!\nentered value is:{value_aggregation_type}')

   #### creating each part of query seperately ####
   
   ## creating date query
   date_key = 'date'
   date_query = []
   for date in dates:
      date_query.append({date_key: date})

   ## creating channels query
   channel_key = 'channel'
   channel_query = []

   for ch in channels:
      channel_query.append({channel_key: ch})
   
   ## creating the account_name query
   account_key = 'account_name'
   account_query = []

   for account in acc_names:
      account_query.append({account_key: account})
   
   #### creating the query ####
   query = {
      '$' + variable_aggregation_type: [
         {'$' + value_aggregation_type: account_query},
         {'$' + value_aggregation_type: channel_query},
         {'$' + value_aggregation_type: date_query}
      ]
   }

   return query

def sum_interactions_features(cursor_list, dict_keys):
   """
   sum the interactions per hour

   Parameters:
   ------------
   cursor_list : list
      the db cursor returned and converted as list
   dict_keys : list
      the list of dictionary keys, representing the features in database
   
   Returns:
   ----------
   summed_counts_per_hour : dictionary
      the dictionary of each feature having summed the counts per hour, the dictionary of features is returned
   """

   summed_counts_per_hour = {}
   for key in dict_keys:
      summed_counts_per_hour[key] = zeros(24)
      
   for key in dict_keys:
      ## the array of hours 0:23
      for data in cursor_list:
         summed_counts_per_hour[key] += data[key]

   return summed_counts_per_hour

def sum_interactions_all(cursor_list, dict_keys):
   """
   sum the interactions per hour, all the interactions will be summed

   Parameters:
   ------------
   cursor_list : list
      the db cursor returned and converted as list
   dict_keys : list
      the list of dictionary keys, representing the features in database
   
   Returns:
   ----------
   summed_counts_per_hour : list
      a list of 1x24 will be returned, showing the 24 hour activity
   """

   summed_counts_per_hour = zeros(24)
      
   for key in dict_keys:
      ## the array of hours 0:23
      ## for each key
      for data in cursor_list:
         summed_counts_per_hour += data[key]

   return summed_counts_per_hour


if __name__ == "__main__":   
   ## hyperparameters
   CONNECTION_STRING = "mongodb://tcmongo:UCk8nV8MuF8v1cM@104.248.137.224:27017/?authMechanism=DEFAULT"
   DB_NAME = '1020707129214111824'
   TABLE = 'heatmaps'

   ## database access
   db_access = DB_access(DB_NAME, CONNECTION_STRING)

   ## sample entries
   channels = ['silly-channel', 'general']
   acc_names = ['yejiisa_furry_578#6257']
   dates = ['2022-12-08', '2023-01-31']

   ## creating the queries
   query =  create_query_sum_interactions(
               acc_names=acc_names,
               channels=channels,
               dates=dates,
               variable_aggregation_type='and',
               value_aggregation_type='or')
   
   ## the features not to be returned 
   ignore_features = {
      'date': 0,
      'account_name': 0, 
      'channel': 0,
      '_id': 0
   }

   cursor = db_access.query_db_find(table=TABLE, query=query, ignore_features=ignore_features)
   cursor_list = list(cursor)

   interactions = sum_interactions_features(cursor_list, cursor_list[0].keys())

   # print(interactions)
   print(interactions["thr_messages"])