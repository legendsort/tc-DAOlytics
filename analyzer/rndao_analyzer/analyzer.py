#!/usr/bin/env python3
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from models.UserModel import UserModel
from models.GuildModel import GuildModel
from models.HeatMapModel import HeatMapModel
from models.RawInfoModel import RawInfoModel
from datetime import datetime
import logging


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
        CONNECTION_STRING = f"mongodb+srv://{self.db_user}:{self.db_password}@cluster0.prmgz21.mongodb.net/?retryWrites=true&w=majority"
        #CONNECTION_STRING = f"mongodb+srv://{self.db_user}:{self.db_password}@{self.db_password}"
        self.db_client = MongoClient(CONNECTION_STRING,
                                     serverSelectionTimeoutMS=10000,
                                     connectTimeoutMS=200000)

        # Model creation
        self.collections["user"] = UserModel(self.db_client.daodb)
        self.collections["guild"] = GuildModel(self.db_client.daodb)
        self.collections["heatmap"] = HeatMapModel(self.db_client.daodb)

    def database_connection_test(self):
        """ Test database connection """
        try:
            # The ping command is cheap and does not require auth.
            self.db_client.admin.command('ping')
        except ConnectionFailure:
            print("Server not available")
            return
        """TODO: Test the authentication"""
        print(self.db_client.list_database_names())

    def run_once(self):
        """ Run analysis once (Wrapper)"""
        self._analyze()

    def _analyze(self):
        """
        Run analysis once (private function)
        """
        pass
        """TODO
        1.) Get the data from the MongoDB
        2.) Parse the data
        3.) Run the analysis scripts on the data
        4.) Push the data back into the MongoDB
        """

    def _test(self):
        """
        A small function to test functionalities when developing.
        Will be removed afterwards
        """
        id = self.collections["user"].insert_one(
            {
                "discordId":"someid",
                "email":"test@email.com",
                "verified":False
            }
        ).inserted_id

        self.collections["guild"].insert_one(
            {
                "guildId":"first_guild",
                "user":id,
                "name":"guild name"
            })
        self.collections["heatmap"].insert_one(
            {
                "date":datetime.now(),
                # "channel":"123",
                # "messages":[1,2,3]
            })




if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    analyzer = RnDaoAnalyzer()
    user = "rndaotest"
    password = "kb9oQKppqEXo6yJ6"
    analyzer.set_database_info(
        db_url="cluster0.prmgz21.mongodb.net/test",
        db_password=password,
        db_user=user
    )
    analyzer.database_connect()
    analyzer.database_connection_test()
    analyzer._test()
