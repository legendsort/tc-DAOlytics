## Test different type of needs using the functions below
from analytics_interactions_script import (sum_interactions_features, 
                               Query,
                               per_account_interactions)
from db_connection import DB_access
from credentials import (
    CONNECTION_STRING,
    DB_NAME,
    TABLE
)


def test_sum_interactions_features(db_access, table, query_dict) -> None:
    ## the features not to be returned 
    ignore_features = {
        'date': 0,
        'account': 0, 
        'channelId': 0,
        'replier_accounts': 0,
        'mentioner_accounts': 0,
        'reacter_accounts': 0,
        '_id': 0
    }

    cursor = db_access.query_db_find(table= table,
                                     query=query_dict,
                                     ignore_features=ignore_features)
    cursor_list = list(cursor)

    interactions = sum_interactions_features(cursor_list=cursor_list, 
                                             dict_keys= cursor_list[0].keys())
    
    print(interactions)

def test_per_account_interactions(db_access, table, query_dict):
    """
    test per account interactions (interactions are `mentioner_accounts`, `reacter_accounts`, and `replier_accounts`)
    """

    ignore_features = {
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


    cursor = db_access.query_db_find(table= table,
                                    query=query_dict,
                                    ignore_features= ignore_features)
    cursor_list = list(cursor)
    results = per_account_interactions(cursor_list=cursor_list)

    print(results)






if __name__=='__main__':

    channels = ['123123123123']
    dates = ['2022-02-01']
    acc_names = ['MagicPalm']

    ## database access
    db_access = DB_access(DB_NAME, CONNECTION_STRING)

    query = Query()
    
    query_dict = query.create_query_filter_account_channel_dates(
        acc_names=acc_names, 
        channels= channels,
        dates=dates)
    

    ########## uncomment this below to test the summing the interactions in 24 hour
    # test_sum_interactions_features(db_access, TABLE, query_dict)


    ########## uncomment this below to test the per account interactions (`mentioner_accounts`, `reacter_accounts`, `replier_accounts`)
    test_per_account_interactions(db_access, TABLE, query_dict)




