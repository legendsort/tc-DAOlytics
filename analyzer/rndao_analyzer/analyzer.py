#!/usr/bin/env python3
import logging
import os
import sys

from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from dateutil import tz
from collections import Counter
# Database models
from models.UserModel import UserModel
from models.GuildModel import GuildModel
from models.HeatMapModel import HeatMapModel
from models.RawInfoModel import RawInfoModel
from models.GuildsRnDaoModel import GuildsRnDaoModel

# Activity hourly
from analysis.activity_hourly import activity_hourly
from dotenv import load_dotenv


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
        self.db_port = ""
        """ Database user -- TODO: Safe implementation to extract user info from env?"""
        """ Use a function instead of the string"""
        self.db_user = ""
        """ Database user password -- TODO: Safe implementation to extract user info from env?"""
        self.db_password = ""
        """ Testing, prevents from data upload"""
        self.testing = False

    def set_database_info(self, db_host: str = "", db_url: str = "", db_user: str = "", db_password: str = "", db_port: str = ""):
        """
        Database information setter
        """
        self.db_url = db_url
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    def database_connect(self):
        """
        Connect to the database
        """
        """ Connection String will be modified once the url is provided"""

        CONNECTION_STRING = f"mongodb://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}"

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

    def run_once(self, guildId):
        """ Run analysis once (Wrapper)"""
        guilds_c = GuildsRnDaoModel(self.db_client["RnDAO"])
        guilds = guilds_c.get_connected_guilds(guildId)

        logging.info(f"Creating heatmaps for {guilds}")
        for guild in guilds:
            self.analysis_heatmap(guild)

    def get_guilds(self):
        """Returns the list of all guilds"""
        logging.info(
            f"Listed guilds {rawinfo_c.database.list_collection_names()}")

    def getNumberOfActions(self, heatmap):
        sum_ac = 0
        fields = ["thr_messages", "lone_messages", "replier",
                  "replied", "mentioned", "mentioner", "reacter", "reacted"]
        for field in fields:
            for i in range(24):
                sum_ac += heatmap[field][i]
        return sum_ac

    def analysis_heatmap(self, guild):
        """
        Based on the rawdata creates and stores the heatmap data
        """
        # activity_hourly()
        if not guild in self.db_client.list_database_names():
            logging.error(f"Database {guild} doesn't exist")
            logging.error(
                f"Existing databases: {self.db_client.list_database_names()}")
            logging.info("Continuing")
            return

        # Collections involved in analysis
        # guild parameter is the name of the database
        rawinfo_c = RawInfoModel(self.db_client[guild])
        heatmap_c = HeatMapModel(self.db_client[guild])

        # Testing if there are entries in the rawinfo collection
        if rawinfo_c.count() == 0:
            logging.warning(
                f"No entries in the collection 'rawinfos' in {guild} databse")
            return

        if not heatmap_c.collection_exists():
            raise Exception(
                f"Collection '{heatmap_c.collection_name}' does not exist")
        if not rawinfo_c.collection_exists():
            raise Exception(
                f"Collection '{rawinfo_c.collection_name}' does not exist")

        last_date = heatmap_c.get_last_date()

        if last_date == None:
            # If no heatmap was created, than tha last date is the first
            # rawdata entry
            last_date = rawinfo_c.get_first_date()
            last_date.replace(tzinfo=timezone.utc)
        else:
            last_date = last_date + timedelta(days=1)

        # Generate heatmap for the days between the last_date and today
        # rawinfo_c.test_get()

        while last_date.astimezone() < datetime.now().astimezone() - timedelta(days=1):
            entries = rawinfo_c.get_day_entries(last_date)
            if len(entries) == 0:
                # analyze next day
                last_date = last_date + timedelta(days=1)
                continue

            prepared_list = []
            account_list = []

            for entry in entries:
                entry["user_mentions"] = entry["user_mentions"][0].split(",")

                prepared_list.append(
                    {
                        # .strftime('%Y-%m-%d %H:%M'),
                        "datetime": entry["datetime"],
                        "channel": entry["channelId"],
                        "author": entry["author"],
                        "replied_user": entry["replied_user"],
                        "user_mentions": entry["user_mentions"],
                        "reactions": entry["reactions"],
                        "thread": entry["thread"],
                        "mess_type": entry["type"],
                    }
                )
                if not entry["author"] in account_list and entry["author"]:
                    account_list.append(entry["author"])

                if entry["user_mentions"] != None:
                    for account in entry["user_mentions"]:
                        if account not in account_list and account:
                            account_list.append(account)

            activity = activity_hourly(prepared_list, acc_names=account_list)
            warnings = activity[0]
            heatmap = activity[1][0]
            # Parsing the activity_hourly into the dictionary
            for heatmap in activity[1]:
                for i in range(len(account_list)):
                    heatmap_dict = {}
                    heatmap_dict["date"] = heatmap["date"][0]
                    heatmap_dict["channelId"] = heatmap["channel"][0]
                    heatmap_dict["thr_messages"] = heatmap["thr_messages"][i]
                    heatmap_dict["lone_messages"] = heatmap["lone_messages"][i]
                    heatmap_dict["replier"] = heatmap["replier"][i]
                    heatmap_dict["replied"] = heatmap["replied"][i]
                    heatmap_dict["mentioner"] = heatmap["mentioner"][i]
                    heatmap_dict["mentioned"] = heatmap["mentioned"][i]
                    heatmap_dict["reacter"] = heatmap["reacter"][i]
                    heatmap_dict["reacted"] = heatmap["reacted"][i]
                    heatmap_dict["reacted_per_acc"] = store_counts_dict(dict(Counter(heatmap["reacted_per_acc"][i])))
                    heatmap_dict["mentioner_per_acc"] = store_counts_dict(dict(Counter(heatmap["mentioner_per_acc"][i])))
                    heatmap_dict["replied_per_acc"] = store_counts_dict(dict(Counter(heatmap["replied_per_acc"][i])))
                    heatmap_dict["account_name"] = heatmap["acc_names"][i]
                    sum_ac = self.getNumberOfActions(heatmap_dict)

                    if not self.testing and sum_ac > 0:
                        heatmap_c.insert_one(heatmap_dict)

            # analyze next day
            last_date = last_date + timedelta(days=1)

# get guildId from command, if not given return None
# python ./analyzer.py guildId


class AccountCounts:
    """
    Class for storing number of interactions per account
    """

    # define constructor
    def __init__(self, account, counts):

        self.account = account  # account name
        self.counts = counts    # number of interactions

    # convert as dict
    def asdict(self):
        return {'account': self.account, 'count': self.counts},

def getGuildFromCmd():
    args = sys.argv
    guildId = None
    if len(args) == 2:
        guildId = args[1]
    return guildId

def store_counts_obj(counts_dict):

    # make empty result array
    obj_array = []

    # for each account
    for acc in counts_dict.keys():

        # make object and store in array
        obj_array.append(AccountCounts(acc, counts_dict[acc]))

    return obj_array

def store_counts_dict(counts_dict):

    # make empty result array
    obj_array = []

    # for each account
    for acc in counts_dict.keys():

        # make dict and store in array
        obj_array.append(AccountCounts(acc, counts_dict[acc]).asdict())

    return obj_array


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    analyzer = RnDaoAnalyzer()
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    analyzer.set_database_info(
        db_url="",
        db_host=host,
        db_password=password,
        db_user=user,
        db_port=port
    )
    guildId = getGuildFromCmd()
    analyzer.database_connect()
    analyzer.run_once(guildId)
