## Test different type of needs using the functions below
from analytics_interactions_script import (sum_interactions_features, 
                               Query,
                               per_account_interactions, 
                               filter_channel_name_id, 
                               filter_channel_thread)
from db_connection import DB_access
from credentials import (
    CONNECTION_STRING,
    DB_NAME,
    TABLE
)


def test_sum_interactions_features(db_access, 
                                   table, 
                                   channels,
                                   dates,
                                   acc_names) -> None:
    ## the features to be or not to be returned 
    feature_projection = {
        'thr_messages': 1,
        'lone_messages': 1,
        'replier': 1,
        'replied': 1,
        'mentioner': 1,
        'mentioned': 1,
        'reacter': 1,
        'reacted': 1,
        '_id': 0
    }
    query = Query()
    
    query_dict = query.create_query_filter_account_channel_dates(
        acc_names=acc_names, 
        channels= channels,
        dates=dates,
        date_key='date',
        channel_key='channelId',
        account_key='account_name'
        )

    cursor = db_access.query_db_find(table= table,
                                     query=query_dict,
                                     feature_projection=feature_projection,
                                     )
    cursor_list = list(cursor)

    interactions = sum_interactions_features(cursor_list=cursor_list, 
                                             dict_keys= cursor_list[0].keys())
    
    print(interactions)

def test_per_account_interactions(db_access, 
                                  table, 
                                  channels,
                                  dates,
                                  acc_names,
                                  dict_keys_list=['replier_accounts', 'reacter_accounts' , 'mentioner_accounts']) -> None:
    """
    test per account interactions (interactions are `mentioner_accounts`, `reacter_accounts`, and `replier_accounts`)
    """

    feature_projection = {
        'thr_messages': 0,
        'lone_messages': 0,
        'replier':0,
        'replied': 0,
        'mentioner': 0,
        'mentioned': 0,
        'reacter': 0,
        'reacted': 0,
        '__v': 0
    }

    query = Query()
    
    query_dict = query.create_query_filter_account_channel_dates(
        acc_names=acc_names, 
        channels= channels,
        dates=dates,
        date_key='date',
        channel_key='channelId',
        account_key='account_name'
        )

    cursor = db_access.query_db_find(table= table,
                                    query=query_dict,
                                    feature_projection = feature_projection)
    cursor_list = list(cursor)
    
    results = per_account_interactions(cursor_list=cursor_list, dict_keys=dict_keys_list)

    print(results)

def test_query_threads(db_access, 
                       table_channel,
                       table_messages, 
                       channel_names,
                       dates, 
                       channelsName_key = 'channel',
                       channelsId_key='channelId', 
                       date_key='date',
                       threadid_key = 'threadId',
                       author_key = 'author',
                       message_content_key = 'content') -> None:
    query = Query()

    ########## first querying to get the channels id from channels name ##########
    channels_projection = {
        'channelId': 1,
        'channel': 1
    } 

    query_channels_dict = query.create_query_channel(channel_names)
    cursor_channels = db_access.query_db_find(table= table_channel,
                                    query=query_channels_dict,
                                    feature_projection = channels_projection)
    
    cursor_channels_list = list(cursor_channels)
    
    if cursor_channels_list == []:
        raise ValueError("No channels available! please first check if the channels you want are available.")

    ## filtering the query to make a dictionary of keys as channel id and values as channel names
    channels_id_dict = filter_channel_name_id(cursor_channels_list, 
                           channelsName_key, 
                           channelsId_key)

    
    ########## And now querying the table with messages in it ##########
    query_dict = query.create_query_threads(
        channels_id=list(channels_id_dict.keys()), 
        dates=dates,
        channelsId_key=channelsId_key,
        date_key=date_key
        )
    
    
    projection = {
        'user_mentions': 0,
        'role_mentions': 0,
        'reactions': 0,
        'replied_user': 0,
        'type': 0,
        'messageId': 0,
        '__v': 0
    }

    cursor = db_access.query_db_find(table= table_messages,
                                    query=query_dict,
                                    feature_projection = projection,
                                    sorting=('datetime', -1)
                                    )
    
    cursor_list = list(cursor)    

    ## getting a result as `channel_thread_dict : {str:{str:{str:str}}}`
    thread_results = filter_channel_thread(cursor_list=cursor_list,
                          channels_name_id_dict=channels_id_dict, 
                          thread_id_key=threadid_key,
                          author_key=author_key,
                          message_content_key=message_content_key)
    
    print(thread_results)





if __name__=='__main__':
    """
    Test the implemented scripts (uncomment each of 3 functions to how each script works and what they output)

    Note that we've made some variables names having `key` because for multiple servers we had different DB schemas
    So by setting each field as the field in DB you can retrieve the results
    """
    # channels = ['123123123123']
    # dates = ['2022-02-01']
    # acc_names = ['MagicPalm']

    channels = ['993163081939165240']
    ## channels_name is used for the test_query_threads 
    channels_name = ['general', 'announcements']
    dates = ['2022-07-10', '2022-08-08', '2022-08-16']
    
    acc_names = ["thegadget.eth#3374"]

    ## database access
    db_access = DB_access(DB_NAME, CONNECTION_STRING)

    

    ########## uncomment this below to test the summing the interactions in 24 hour
    # test_sum_interactions_features(db_access, 
    #                                TABLE,
    #                                channels,
    #                                dates,
    #                                acc_names)


    ########## uncomment this below to test the per account interactions (`mentioner_accounts`, `reacter_accounts`, `replier_accounts`)
    # test_per_account_interactions(db_access, 
    #                               TABLE, 
    #                               channels,
    #                               dates,
    #                               acc_names,
    #                               dict_keys_list=['replied_per_acc', 'reacted_per_acc' , 'mentioner_per_acc']
    #                               )


    ########## uncomment this below to test the per thread messages
    test_query_threads(db_access=db_access,
                       table_channel='channels',
                       table_messages='rawinfos',
                       channel_names=channels_name, 
                       dates=dates, 
                       date_key='datetime',
                       )





