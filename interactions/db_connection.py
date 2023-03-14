from pymongo import MongoClient

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
   
