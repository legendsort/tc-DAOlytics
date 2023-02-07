#!/usr/bin/env python3
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from models.UserModel import UserModel
from models.GuildModel import GuildModel
from models.HeatMapModel import HeatMapModel
from models.RawInfoModel import RawInfoModel
from datetime import datetime, timedelta, timezone
from analysis.activity_hourly import activity_hourly
import logging
import json
from dateutil import tz


class RnDaoAnalyzer:
    """
    RnDaoAnalyzer
    class that handles database connection and data analysis
    """
    def __init__(self):
        """
        Class initiation function
        """
        """ MongoDB client """
        self.db_client = None
        """ Database URL """
        self.db_url = ""
        """ Database user -- TODO: Safe implementation to extract user info from env?"""
        """ Use a function instead of the string"""
        self.db_user = ""
        """ Database user password -- TODO: Safe implementation to extract user info from env?"""
        self.db_password = ""
        """ Analysis frequency: if -1 then its infinite"""
        self.models = []
        self.collections = {
            "user": None,
            "guild":None,
            "heatmap":None,
        }


    def set_database_info(self, db_url:str="",db_user:str="",db_password:str=""):
        """
        Database information setter
        """
        self.db_url=db_url
        self.db_user = db_user
        self.db_password = db_password


    def database_connect(self):
        """
        Connect to the database
        """
        """ Connection String will be modified once the url is provided"""
        #CONNECTION_STRING = f"mongodb+srv://{self.db_user}:{self.db_password}@cluster0.mgy22jx.mongodb.net/test"
        CONNECTION_STRING = f"mongodb+srv://root:root@cluster0.mgy22jx.mongodb.net/test"

        #CONNECTION_STRING = f"mongodb+srv://{self.db_user}:{self.db_password}@{self.db_password}"
        self.db_client = MongoClient(CONNECTION_STRING,
                                     serverSelectionTimeoutMS=10000,
                                     connectTimeoutMS=200000)

        # Model creation
        #print(self.db_client.RnDAO.list_collection_names())
        # self.collections["user"] = UserModel(self.db_client.RnDAO)
        # self.collections["guild"] = GuildModel(self.db_client.RnDAO)
        # self.collections["heatmap"] = HeatMapModel(self.db_client.RnDAO)

    def database_connection_test(self):
        """ Test database connection """
        try:
            # The ping command is cheap and does not require auth.
            self.db_client.admin.command('ping')
        except ConnectionFailure:
            print("Server not available")
            return
        """TODO: Test the authentication"""
        print("Databases:")
        print(self.db_client.list_database_names())
        print("Guild 1")
        print(self.db_client["guildId#1"].list_collection_names())


    def run_once(self, guild):
        """ Run analysis once (Wrapper)"""
        self._analyze(guild)

    def analysis_heatmap(self, guild):
        """
        Based on the rawdata creates and stores the heatmap data
        """
        #activity_hourly()
        if not guild in self.db_client.list_database_names():
            raise Exception("Chosen database does not exist")
        else:
            print("Database exists")

        # Collections involved in analysis
        rawinfo_c = RawInfoModel(self.db_client[guild])
        heatmap_c = HeatMapModel(self.db_client[guild])

        if not heatmap_c.is_present():
            raise Exception(f"Collection '{heatmap_c.collection_name}' does not exist")
        if not rawinfo_c.is_present():
            raise Exception(f"Collection '{rawinfo_c.collection_name}' does not exist")


        # for document in rawinfo_c.get_all():
        #     print(document)

        # print("################################################")

        # for document in heatmap_c.get_all():
        #     print(document)

        # The last date heatmap created for
        last_date = heatmap_c.get_last_date()
        last_date = None
        last_date = datetime(2023,1,1,0,0,0).astimezone()
        if last_date == None:
            # If no heatmap was created, than tha last date is the first
            # rawdata entry
            last_date = rawinfo_c.get_first_date()
            last_date.replace(tzinfo=timezone.utc)

        # Generate heatmap for the days between the last_date and today
        #rawinfo_c.test_get()
        while last_date.astimezone() < datetime.now().astimezone()-timedelta(days=1):
            print(last_date)
            entries = rawinfo_c.get_day_entries(last_date)
            if len(entries)==0:
                # analyze next day
                last_date = last_date + timedelta(days=1)
                continue

            #Prepare the list
            prepared_list = []
            account_list = []

            for entry in entries:
                prepared_list.append(
                    {
                        "datetime": entry["created_at"].strftime('%Y-%m-%d %H:%M'),
                        "channel" : entry["channelId"],
                        "author"  : entry["author"],
                        "replied_user": entry["replied_User"],
                        "user_mentions": entry["user_Mentions"],
                        "reactions" : entry["reactions"],
                        "thread" : None,
                        "mess_type": entry["type"],
                    }
                )
                if not entry["author"] in account_list:
                    account_list.append(entry["author"])

                for account in entry["user_Mentions"]:
                    if account not in account_list:
                        account_list.append(account)

            activity = activity_hourly(prepared_list, acc_names=account_list)
            warnings = activity[0]
            heatmap = activity[1][0]
            # Parsing the activity_hourly into the dictionary
            heatmap_dict = {}
            heatmap_dict["date"] = heatmap["date"]
            heatmap_dict["channel"] = heatmap["channel"]
            heatmap_dict["thr_messages"] = heatmap["thr_messages"]
            heatmap_dict["lone_messages"] = heatmap["lone_messages"]
            heatmap_dict["replier"] = heatmap["replier"]
            heatmap_dict["replied"] = heatmap["replied"]
            heatmap_dict["mentioner"] = heatmap["mentioner"]
            heatmap_dict["mentioned"] = heatmap["mentioned"]
            heatmap_dict["reacter"] = heatmap["reacter"]
            heatmap_dict["reacted"] = heatmap["reacted"]
            heatmap_dict["account_names"] = account_list

            heatmap_c.insert_one(heatmap_dict)

            # analyze next day
            last_date = last_date + timedelta(days=1)


    def _analyze(self, guild):
        """
        Run analysis once (private function)
        """
        """TODO
        1.) Get the data from the MongoDB
        2.) Parse the data
        3.) Run the analysis scripts on the data
        4.) Push the data back into the MongoDB
        """

        if not guild in self.db_client.list_database_names():
            raise Exception("Chosen database does not exist")
        else:
            print("Database exists")

        # Collections involved in analysis
        rawinfo_c = RawInfoModel(self.db_client[guild])
        heatmap_c = HeatMapModel(self.db_client[guild])

        if not heatmap_c.is_present():
            raise Exceptino(f"Collection '{heatmap_c.collection_name}' does not exist")
        if not rawinfo_c.is_present():
            raise Exceptino(f"Collection '{rawinfo_c.collection_name}' does not exist")

        for document in rawinfo_c.get_all():
            print("--------------------------------------------------")
            print(document)
            print("--------------------------------------------------")


    def _test(self):
        """
        A small function to test functionalities when developing.
        Will be removed afterwards
        """




if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    analyzer = RnDaoAnalyzer()
    #user = "rndaotest"
    #password = "kb9oQKppqEXo6yJ6"
    #url="cluster0.prmgz21.mongodb.net/test",
    user = "tcmongo"
    password = "T0g3th3rCr3wM0ng0P55"

    analyzer.set_database_info(
        db_url="",
        db_password=password,
        db_user=user
    )
    analyzer.database_connect()
    #analyzer.database_connection_test()
    #analyzer._test()
    analyzer.analysis_heatmap('guildId#1')
