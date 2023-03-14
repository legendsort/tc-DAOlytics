from numpy import zeros, squeeze


class Query():

    def __init__(self) -> None:
        """
        create different queries to query the database
        """
        pass


    
    def _check_inputs(self, acc_names, channels, dates, variable_aggregation_type='and', value_aggregation_type='or'):
        """
        just check whether the inputs are correctly entered or not 
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

    def create_query_filter_account_channel_dates(self, 
                                                  acc_names,
                                                  channels, 
                                                  dates, 
                                                  variable_aggregation_type='and', 
                                                  value_aggregation_type='or',
                                                  date_key='date',
                                                  channel_key='channelId',
                                                  account_key = 'account'):
        """
        A query to filter the database on account_name, and/or channel_names, and/or dates 
        the aggregation of varibales (`account_name`, `channels`, and `dates`) can be set to `and` or `or`
        

        Parameters:
        ------------
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
        date_key : string
            the name of the field of date in database
            default is `date`
        channel_key : string
            the id of the field of channel name in database
            default is `channelId`
        account_key : string
            the name of the field account name in the database
            default is `account`

        Returns:
        ----------
        query : dictionary
            the query to get access
        """

        #### creating each part of query seperately ####
        
        ## creating date query
        date_query = []
        for date in dates:
            date_query.append({date_key: {'$regex': date}})

        ## creating channels query
        channel_query = []

        for ch in channels:
            channel_query.append({channel_key: ch})
        
        ## creating the account_name query
        account_query = []

        for account in acc_names:
            account_query.append({account_key: account})
        
        #### creating the query ####
        query = {
            '$' + variable_aggregation_type: [
                {'$' + value_aggregation_type: account_query},
                {'$' + value_aggregation_type: channel_query},
                ## for time we should definitly use `or` because `and` would result in nothing!
                {'$or': date_query}
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


def per_account_interactions(cursor_list, 
                             dict_keys=['replier_accounts', 'reacter_accounts', 'mentioner_accounts'],
                             ):
    """
    get per account interactions as `mentioner_accounts`, `reacter_accounts`, and `replier_accounts` (summing)

    Parameters:
    ------------
    cursor_list : list
        the db cursor returned and converted as list
    dict_keys : list
        the list of dictionary keys, representing the features in database

    Returns:
    ----------
    summed_per_account_interactions : dictionary
        the dictionary of each feature having summed the counts per hour, the dictionary of features is returned
    """

    per_acc_interactions = {}

    ## initialze the fields of the dictionary
    for feature in dict_keys:
        per_acc_interactions[feature] = {}

    ## for each feature
    for feature in dict_keys:
        ## for each record retrieved from DB
        for db_records in cursor_list:
            ## for each interactor type in record
            for db_interactor in db_records[feature]:
                
                ## because of DB inconsistency
                ## there was a list of one item always in one of the servers
                ## so we're getting the first or the one item available of it
                if type(db_interactor) is list:
                    db_interactor_ = db_interactor[0]
                ## else, if the inconsistency wasn't available
                else:
                    db_interactor_ = db_interactor
                
                acc_name = db_interactor_['account']
                ## if the account wasn't available in saved dictionary
                ## then simply set the counts to the saved dictionary 
                if acc_name not in per_acc_interactions[feature].keys():
                    per_acc_interactions[feature][acc_name] = db_interactor_['count']
                ## else, sum the count to it
                else:
                    per_acc_interactions[feature][acc_name] += db_interactor_['count']

    ## remaking the dictionaries into the format of database

    per_acc_interactions_db_style = {}
    all_interactions_per_acc = {}


    ## for the interaction type, e.g.: `replier_accounts`
    for key in per_acc_interactions.keys():
        per_acc_interactions_db_style[key] = {}

        ## for each account which is saved as a key
        for idx, acc_name in enumerate(per_acc_interactions[key].keys()):
            
            interaction_count = per_acc_interactions[key][acc_name]
            per_acc_interactions_db_style[key][idx] = {
                'account': acc_name,
                'count': interaction_count}

            
            
            ## if the account was available in the dictionary of all interactions
            if acc_name in all_interactions_per_acc.keys():
                all_interactions_per_acc[acc_name] += interaction_count
            ## else it wasn't available, then create the account with its interaction count
            else:
                all_interactions_per_acc[acc_name] = interaction_count


    per_acc_interactions_db_style['all_interaction_accounts'] = {}

    ## adding the all interactions_per_acc to one dictionary
    for idx, acc_name in enumerate(all_interactions_per_acc.keys()):
        per_acc_interactions_db_style['all_interaction_accounts'][str(idx)] = {
            'account': acc_name,
            'count': all_interactions_per_acc[acc_name]
        }

    summed_per_account_interactions = per_acc_interactions_db_style

    return summed_per_account_interactions