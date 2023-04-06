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
from models.MemberActivityModel import MemberActivityModel

# Activity hourly
from analysis.activity_hourly import activity_hourly
from analysis.member_activity_history import member_activity_history
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
            self.analysis_member_activity(guild)

    def get_guilds(self):
        """Returns the list of all guilds"""
        logging.info(
            f"Listed guilds {rawinfo_c.database.list_collection_names()}")

    # get detailed info from one guild
    def get_one_guild(self, guild):
        """Get one guild setting from guilds collection by guild"""
        guild_c = GuildsRnDaoModel(self.db_client["RnDAO"])
        result = guild_c.get_guild_info(guild)
        return result

    # insert all elements in child_arr to parent_arr which are not in parent_arr,
    def merge_array(self, parent_arr, child_arr):
        for element in child_arr:
            if element == '':
                continue
            if element not in parent_arr:
                parent_arr.append(element)

    def parse_reaction(self, s):
        result = []
        for subitem in s:
            items = subitem.split(',')
            parsed_items = []
            for item in items:
                parsed_items.append(item)
            self.merge_array(result, result[:-1])
        return result

    # get all users from one day messages
    def get_users_from_oneday(self, entries):
        users = []
        for entry in entries:
            # author
            if entry["author"]:
                self.merge_array(users, [entry["author"]])
            # mentioned users
            mentions = entry["user_mentions"][0].split(",")
            self.merge_array(users, mentions)
            # reacters
            reactions = self.parse_reaction(entry["reactions"])
            self.merge_array(users, reactions)
        return users

    # get all user accounts during date_range in guild from rawinfo data
    def get_all_users(self, guild, date_range, rawinfo_c):
        # check guild is exist
        if not guild in self.db_client.list_database_names():
            logging.error(f"Database {guild} doesn't exist")
            logging.error(
                f"Existing databases: {self.db_client.list_database_names()}")
            logging.info("Continuing")
            return []
        all_users = []

        day = date_range[0]
        # iterate everyday in date range
        while day.astimezone() <= date_range[1].astimezone():
            entries = rawinfo_c.get_day_entries(day)
            users = self.get_users_from_oneday(entries)
            # insert all users to all_users who are not in all_users
            self.merge_array(all_users, users)
            day = day + timedelta(days=1)

        return all_users

    # get number of actions
    def getNumberOfActions(self, heatmap):
        sum_ac = 0
        fields = ["thr_messages", "lone_messages", "replier",
                  "replied", "mentioned", "mentioner", "reacter", "reacted"]
        for field in fields:
            for i in range(24):
                sum_ac += heatmap[field][i]
        return sum_ac

    def analysis_member_activity(self, guild):
        """
        Based on the rawdata creates and stores the member activity data
        """

        # check current guild is exist
        if not guild in self.db_client.list_database_names():
            logging.error(f"Database {guild} doesn't exist")
            logging.error(
                f"Existing databases: {self.db_client.list_database_names()}")
            logging.info("Continuing")
            return

        member_activity_c = MemberActivityModel(self.db_client[guild])
        rawinfo_c = RawInfoModel(self.db_client[guild])

        # Testing if there are entries in the rawinfo collection
        if rawinfo_c.count() == 0:
            logging.warning(
                f"No entries in the collection 'rawinfos' in {guild} databse")
            return

        # get current guild setting
        setting = self.get_one_guild(guild)
        CONNECTION_STRING = f"mongodb://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}"
        channels, window, action = setting["selectedChannels"], setting["window"], setting["action"]
        channels = list(map(lambda x: x["channelId"], channels))

        # get date range to be analyzed
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if member_activity_c.count() == 0:
            """This is the first analysis"""
            first_date = rawinfo_c.get_first_date().replace(
                hour=0, minute=0, second=0, microsecond=0)
            last_date = today - timedelta(days=1)
        else:
            """This is a daily analysis"""
            first_date = member_activity_c.get_last_date().replace(
                hour=0, minute=0, second=0, microsecond=0)
            first_date = first_date + timedelta(days=1)
            last_date = first_date + timedelta(days=6)

        while last_date.astimezone() < today.astimezone():
            date_range = [first_date, last_date]
            # get all users during date_range
            all_users = self.get_all_users(guild, date_range, rawinfo_c)
            # change format like 23/03/27
            date_range = [dt.strftime("%y/%m/%d") for dt in date_range]
            network, activities = member_activity_history(
                guild, CONNECTION_STRING, channels, all_users, date_range, window, action)
            for activity in activities:
                member_activity_c.insert_one(activity)

            first_date += timedelta(days=1)
            last_date += timedelta(days=1)
        # create member activity document
        return True

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
            if last_date == None:
                raise Exception(
                    f"Collection '{rawinfo_c.collection_name}' does not exist")
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
                    heatmap_dict["reacted_per_acc"] = store_counts_dict(
                        dict(Counter(heatmap["reacted_per_acc"][i])))
                    heatmap_dict["mentioner_per_acc"] = store_counts_dict(
                        dict(Counter(heatmap["mentioner_per_acc"][i])))
                    heatmap_dict["replied_per_acc"] = store_counts_dict(
                        dict(Counter(heatmap["replied_per_acc"][i])))
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
