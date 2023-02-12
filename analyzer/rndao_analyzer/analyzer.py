#!/usr/bin/env python3
import logging
import json
import os

from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from dateutil import tz
# Database models
from models.UserModel import UserModel
from models.GuildModel import GuildModel
from models.HeatMapModel import HeatMapModel
from models.RawInfoModel import RawInfoModel
from models.GuildsRnDaoModel import GuildsRnDaoModel

# Activity hourly
from analysis.activity_hourly import activity_hourly

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
        self.db_host = ""
        """ Database user -- TODO: Safe implementation to extract user info from env?"""
        """ Use a function instead of the string"""
        self.db_user = ""
        """ Database user password -- TODO: Safe implementation to extract user info from env?"""
        self.db_password = ""
        """ Testing, prevents from data upload"""
        self.testing = False


    def set_database_info(self,db_host:str="", db_url:str="",db_user:str="",db_password:str=""):
        """
        Database information setter
        """
        self.db_url=db_url
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host


    def database_connect(self):
        """
        Connect to the database
        """
        """ Connection String will be modified once the url is provided"""
        CONNECTION_STRING  = f"mongodb://{self.db_user}:{self.db_password}@{self.db_host}"

        self.db_client = MongoClient(CONNECTION_STRING,
                                     serverSelectionTimeoutMS=10000,
                                     connectTimeoutMS=200000)


    def database_connection_test(self):
        """ Test database connection """
        try:
            # The ping command is cheap and does not require auth.
            self.db_client.admin.command('ping')
        except ConnectionFailure:
            logging.error("Server not available")
            return
        #print(self.db_client["guildId#1"].list_collection_names())

    def run_once(self):
        """ Run analysis once (Wrapper)"""
        guilds_c = GuildsRnDaoModel(self.db_client["RnDAO"])
        guilds = guilds_c.get_connected_guilds()
        logging.info(f"Creating heatmaps for {guilds}")
        for guild in guilds:
            self.analysis_heatmap(guild)

    def get_guilds(self):
        """Returns the list of all guilds"""
        print(rawinfo_c.database.list_collection_names())

    def analysis_heatmap(self, guild):
        """
        Based on the rawdata creates and stores the heatmap data
        """
        #activity_hourly()
        if not guild in self.db_client.list_database_names():
            #print(f"Existing databases: {self.db_client.list_database_names()}")
            logging.error(f"Database {guild} doesn't exist")
            logging.error(f"Existing databases: {self.db_client.list_database_names()}")
            logging.info("Continuing")
            return

        # Collections involved in analysis
        # guild parameter is the name of the database
        rawinfo_c = RawInfoModel(self.db_client[guild])
        heatmap_c = HeatMapModel(self.db_client[guild])

        if not heatmap_c.collection_exists():
            raise Exception(f"Collection '{heatmap_c.collection_name}' does not exist")
        if not rawinfo_c.collection_exists():
            raise Exception(f"Collection '{rawinfo_c.collection_name}' does not exist")

        last_date = heatmap_c.get_last_date()
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
            if not self.testing:
                heatmap_c.insert_one(heatmap_dict)

            # analyze next day
            last_date = last_date + timedelta(days=1)





if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    analyzer = RnDaoAnalyzer()
    user = os.getenv("RNDAO_DB_USER")
    password = os.getenv("RNDAO_DB_PASSWORD")
    host = os.getenv("RNDAO_DB_HOST")
    print(user, password, host)
    analyzer.set_database_info(
        db_url="",
        db_host=host,
        db_password=password,
        db_user=user
    )
    analyzer.database_connect()
    analyzer.run_once()
