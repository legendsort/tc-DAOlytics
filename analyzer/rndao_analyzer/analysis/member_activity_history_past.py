## checking the past history of member activities
    
######################## The whole process is as follows ########################
    ## 1. first query the db to see the `first_end_date`
    ##      if the `first_end_date` was in `date_range` then
    ##       - First add the available data in the date range of `[first_end_date, date_end]` from the DB to the dictionaries of activities
    ##       - Then go throught the codes of *Actuall Analysis* with a new `date_range` (omit the dates before the `first_end_date`)
    ##       - Also we should modify the `w_i` not to start from zero
    ##          + To do this we could easily find the maximum key in the db queries 


## Importing libraries
import datetime
import numpy as np
from dateutil import parser


## the main script function
def check_past_history(db_access, 
                       date_range, 
                       activity_names_list=None,
                       TABLE_NAME='memberactivities',
                       verbose=False):
    """
    check past member_activities history and return if some analysis were available in db in the date_range

    Parameters:
    -------------
    db_access: DB_access
        the database access class that queries are called through it
    date_range: list of strings
        a list of length 2, the first index has the start of the interval
        and the second index is end of the interval
        *Note*: Each value of the array should be in the format of `str(%y/%m/%d)`
    activity_names_list : list of strings
        the list of activities available in db
        if `None` will use the actitities in db, defualt is `None`
        This is added if we wanted to filter the activities, as default all activities are available in db
    TABLE_NAME: string
        the table of db to use
        default is `memberactivities`
    verbose : bool
        whether to print the logs or not

    Returns:
    ----------
    all_activity_data_dict : dictionary
        the data for past activities
    new_date_range : list
        list of new date range in datetime format
        because the last 
    maximum_key : int
        the maximum key that the new data should start its data from
    """
    ## checking the inputs
    if len(date_range) != 2:
        raise ValueError(f"""date_range should have the length of two,
          first index is the start of the interval and the second index is the end of the interval
          its length is: {len(date_range)}""")
    
    ## creating the query
    query = create_past_history_query(date_range)
    
    ## do not project the variables that we don't need
    feature_projection = {
        # 'first_end_date': 1,
        # 'all_consistent': 1,
        '_id': 0
    }
    ## sorting the results from past to now (ascending)
    ## sorting by `date` 
    sorting = ['date', 1]

    ## quering the db now
    cursor = db_access.query_db_find(TABLE_NAME, 
                        query,
                        feature_projection,
                        sorting
                        )
    ## getting a list of returned data
    past_data = list(cursor)

    ## if any past data was available in DB
    if past_data != []:
        if verbose: 
            print(past_data)

        db_analysis_start_date = parser.parse(past_data[0]['date'])
        db_analysis_end_date = parser.parse(past_data[-1]['date'])

        days_after_analysis_start = (db_analysis_start_date - db_analysis_end_date).days


        past_data = convert_back_to_old_schema(past_data)

        # days_after_analysis_start = int(max(list(past_data['all_consistent'].keys())))
        # db_analysis_end_date = db_analysis_start_date + datetime.timedelta(days=days_after_analysis_start)
    else:
        db_analysis_start_date = None
        db_analysis_end_date = None

    ## the input date_range in format of datetime
    ## converting the dates into datetime format
    date_format = '%y/%m/%d'
    date_range_start = datetime.datetime.strptime(date_range[0], date_format)
    date_range_end = datetime.datetime.strptime(date_range[1], date_format)
    

    ## if for the requested date_range, its results were available in db 
    if (db_analysis_end_date is not None) and (date_range_start < db_analysis_end_date):

        ## refine the dates
        ## if the range end was smaller than the analysis end, then empty the new_date_range
        ## empty it, since all the requested analysis are available in db
        if date_range_end < db_analysis_end_date:
            new_date_range = []
        else:
            new_date_range = [db_analysis_end_date, date_range_end]

        ## if the activity_names_list wasn't given
        ## then just stick to the activities that were available in db
        ## Note: all activities should always be in db, 
        ### but filtering the activities if wanted we just made it this way
        if activity_names_list is None:
            activity_names_list_ = list(past_data.keys())
            ## removing date since we don't need it anymore
            activity_names_list_.remove('first_end_date')
        ## else if the activity_names_list was given as input
        else:
            activity_names_list_ = activity_names_list
        
        # append the activities data together with increasing indexes
        ## maximum key is used for having the key for future data
        all_activity_data_dict, maximum_key = append_all_past_data(past_data, activity_names_list_, days_after_analysis_start)
    else:
        all_activity_data_dict = {}
        new_date_range = [date_range_start, date_range_end]
        maximum_key = 0


    return all_activity_data_dict, new_date_range, maximum_key



def create_past_history_query(date_range):
    """
    create a query to retreive the data that are not analyzed

    Parameters:
    -------------
    date_range: list
        a list of length 2, the first index has the start of the interval
        and the second index is end of the interval
    
    Returns:
    ----------
    query : dictionary
        the query representing the dictionary of filters
    """
    date_interval_start = datetime.datetime.strptime(date_range[0], '%y/%m/%d').isoformat()
    date_interval_end = datetime.datetime.strptime(date_range[1], '%y/%m/%d').isoformat()

    query = { 
        'date': {
            ## the given date_range in script analysis
            '$gte': date_interval_start,
            '$lte': date_interval_end
        } 
    }

    return query

def convert_back_to_old_schema(retrieved_data):
    """
    convert the retrieved data back to the old schema we had, to do the analysis

    Parameters:
    ---------------
    retrieved_data : array
        array of db returned records
    
    Returns:
    ----------
    activity_dict : dict
        the data converted to the old db schema
    """
    # make empty result dictionary
    activity_dict = {}

    # store results in dictionary
    activity_dict["all_joined"] = {}
    activity_dict["all_consistent"] = {}
    activity_dict["all_vital"] = {}
    activity_dict["all_active"] = {}
    activity_dict["all_connected"] = {}
    activity_dict["all_paused"] = {}
    activity_dict["all_new_disengaged"] = {}
    activity_dict["all_disengaged"] = {}
    activity_dict["all_unpaused"] = {}
    activity_dict["all_returned"] = {}
    activity_dict["all_new_active"] = {}
    activity_dict["all_still_active"] = {}

    ## getting `first_end_date` datetime object
    start_dt = parser.parse(retrieved_data[0]['date'])

    for idx, db_record in enumerate(retrieved_data):
        for activity in activity_dict.keys():
                if db_record[activity] != []:
                    ## creating a dictionary of users
                    users_name = db_record[activity]
                    users_count = range(len(users_name))
                    ## make a dictionary of indexes and users for a specific activity in an specific day
                    # activity_dict[activity][str(idx)] = dict(zip(users_count, users_name))
                    activity_dict[activity][str(idx)] = users_name

    activity_dict['first_end_date'] = start_dt.isoformat()

    return activity_dict


def append_all_past_data(retrived_past_data, activity_names_list, starting_idx=0):
    """
    Append all past activities together

    Parameters:
    --------------
    retrived_past_data : list
        list of dictionaries, having all the activities in it
    activity_names_list : list
        the activities to filter
    starting_idx : int
        the data of activities that should be started from the index
        in another words it would be started from which day
        default is 0, meaning all the past data from the starting point of `first_end_date` will be included

    Returns:
    ----------
    all_activity_data_dict : dictionary
        the analyzed data with refined keys
    maximum_key : int
        the maximum key of the data
    """
    all_activity_data_dict = {}
    maximum_key_values = []
    for activity_name in activity_names_list:
        ## getting all the activities of the list together
        # activity_data_map = map(lambda data_dict: data_dict[activity_name], retrived_past_data)
        # activity_data_list = list(activity_data_map)
        activity_data_list = retrived_past_data[activity_name]
        
        ## making all the dictionary in the list to one dictionary with refined keys
        # activity_data_dict = map( refine_dict_indexes ,activity_data_list)
        activity_data_dict, max_key_val = refine_dict_indexes(activity_data_list, starting_idx)

        maximum_key_values.append(max_key_val)
        ## add it to the new dictionary
        all_activity_data_dict[activity_name] = activity_data_dict

    return all_activity_data_dict, max(maximum_key_values)

def refine_dict_indexes(data_dict, starting_idx=0):
    """
    refine the indexes in dictionary

    Parameters:
    ------------
    data_dict : dictionary
        dictionary for a specific activity with keys '0','1', '2', etc
    starting_idx : int
        the data of activities that should be started from the index
        in another words it would be started from which day
        default is 0, meaning all the past data from the starting point of `first_end_date` will be included

    Returns:
    -----------
    data_dict_appended: dictionary
        all the dictionaries appended together
        the keys are refined in a way that starting with '0' and ending with sum of keys
    max_key_val : int
        the maximum value of the dictionary
    """
    data_dict_appended = {}
    max_key_val = 0
    # ## for each activity dictionary
    # for dictionary in data_dict_list:
    #     ## if the dictionary was not empty, do the followings
    #     if dictionary != {}:

    ## get all the keys in integer format
    indices_list = list(map(lambda x: int(x) ,data_dict.keys()))
    ## converting to numpy to be able to filter them
    indices_list = np.array(indices_list)
    ## filtering them
    indices_list = indices_list[indices_list > starting_idx]
    ## incrementing and converting the indices of the dictionary to string  
    indices_list = list(map(lambda x: str(x + max_key_val), indices_list))
    ## creating new dictionary with new indices
    dictionary_refined_keys = dict(zip( indices_list, list(data_dict.values()) ))
    ## adding it to the results dictionary
    data_dict_appended.update(dictionary_refined_keys)
    
    ## if there was some index available
    if len(indices_list) != 0:
        max_key_val += int(max(indices_list))
    
    return data_dict_appended, max_key_val
