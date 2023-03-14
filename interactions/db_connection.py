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

   def _db_call(self, calling_function, query, feature_projection=None, sorting=None):
      """
      call the function on database, it could be whether aggragation or find

      Parameters:
      -------------
      calling_function : function
         can be `MongoClient.find` or `MongoClient.aggregate`
      query : dictionary
         the query as a dictionary
      feature_projection : dictionary
         the dictionary to or not to project the results on it
         default is None, meaning to return all features
      sorting : tuple
         sort the results base on the input dictionary
         if None, then do not sort the results

      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query 
      """
      ## if there was no projection available
      if feature_projection is None:
         ## if sorting was given
         if sorting is not None:
            cursor = calling_function(query).sort(sorting[0], sorting[1])
         else: 
            cursor = calling_function.find(query)
      else:
         if sorting is not None:
            cursor = calling_function(query, feature_projection).sort(sorting[0], sorting[1])
         else:
            cursor = calling_function(query, feature_projection)

      return cursor

   
   def query_db_aggregation(self, query, table, feature_projection=None, sorting=None):
      """
      aggregate the database using query

      Parameters:
      ------------
      table : string
         the table name to retrieve the data
      query : dictionary
         the query as a dictionary
      feature_projection : dictionary
         the dictionary to or not to project the results on it
         default is None, meaning to return all features

      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query 
      """

      cursor = self._db_call(calling_function=self.db_client[table].aggregate,
                             query=query,
                             feature_projection=feature_projection,
                             sorting=sorting)

      return cursor
  
   def query_db_find(self, table, query, feature_projection=None, sorting=None):
      """
      aggregate the database using query

      Parameters:
      ------------
      table : string
         the table name to retrieve the data
      query : dictionary
         the query as a dictionary
      feature_projection : dictionary
         the dictionary to or not to project the results on it
         default is None, meaning to return all features

      Returns:
      ----------
      cursor : mongodb Cursor
         cursor to get the information of a query 
      """
      cursor = self._db_call(calling_function=self.db_client[table].find, 
                             query=query,
                             feature_projection=feature_projection,
                             sorting=sorting)
      return cursor
   
