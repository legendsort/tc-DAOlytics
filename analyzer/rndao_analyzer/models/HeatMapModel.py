#!/usr/bin/env python3
import logging
from typing import TypedDict
import pymongo
from datetime import datetime, timezone, timedelta

class HeatMapModel():
    def __init__(self, database=None):
        if database is None:
            logging.info("Database does not exist.")
            print("NOT HERE")
            raise Exception("Database should not be None")
        self.database = database
        self.collection_name = "heatmaps"
        self.exists = False
        self.validator = {
            "$jsonSchema" :{
                "bsonType": "object",
                "properties":{
                    "date":{
                        "bsonType": "date",
                    },
                    "channel":{
                        "bsonType": "string",
                    },
                    "lone_messages":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "thr_messages":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "replier":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "replied":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "mentioner":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "mentioned":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "mentioned":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "reacter":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "reacted":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "acc_names":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"string"
                        }
                    }
                }
            }
        }

    def is_present(self):
        if self.collection_name in self.database.list_collection_names():
            return True
        else:
            return False


    def _create_collection_if_not_exists(self):
        logging.info(f"Check if collection {self.collection_name} exists in database")
        if self.collection_name in self.database.list_collection_names():
           logging.info(f"Collection {self.collection_name} exists")
        else:
           logging.info(f"Collection {self.collection_name} doesn't exist")
           result = self.database.create_collection(self.collection_name)
           logging.info(result)
        self.database.command("collMod", self.collection_name, validator=self.validator)
        self.collection = self.database.heatmaps
        self.exists = True

    def insert_one(self, obj_dict):
        if not self.exists:
            self._create_collection_if_not_exists()

        logging.info(f"Inserting guild object into the {self.collection_name} collection.")
        return self.collection.insert_one(obj_dict)

    def get_one(self):
        return self.database[self.collection_name].find_one()

    def get_all(self):
        return self.database[self.collection_name].find()

    def get_last_date(self):
        try:
            date_str = self.database[self.collection_name].find().sort([("date", pymongo.DESCENDING)]).limit(1)[0]["date"]

            #Parsing the time and timezone
            date_str = date_str.split(" GMT")
            date_str[1] = "GMT"+date_str[1]
            date_str[1] = date_str[1].split(" ")[0].replace("GMT","")
            zone = [date_str[1][0:3], date_str[1][3::]]
            zone_hrs = int(zone[0])
            zone_min = int(zone[1])
            date_obj = datetime.strptime(date_str[0], "%a %b %d %Y %H:%M:%S").replace(
                tzinfo=timezone(timedelta(hours=zone_hrs, minutes=zone_min))
            )
            return date_obj
        except Exception():
            print("No database entry with valid field 'date' found")
            return None


class HeatMapModelOld():
    def __init__(self, database=None):
        if database is None:
            logging.info("Database does not exist.")
            print("NOT HERE")
            raise Exception("Database should not be None")
        self.database = database
        self.collection_name = "heatmaps"
        self.exists = False
        self.validator = {
            "$jsonSchema" :{
                "bsonType": "object",
                "properties":{
                    "date":{
                        "bsonType": "date",
                    },
                    "channel":{
                        "bsonType": "string",
                    },
                    "messages":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "interactions":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                    "emojis":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"int"
                        }
                    },
                }
            }
        }

    def is_present(self):
        if self.collection_name in self.database.list_collection_names():
            return True
        else:
            return False


    def _create_collection_if_not_exists(self):
        logging.info(f"Check if collection {self.collection_name} exists in database")
        if self.collection_name in self.database.list_collection_names():
           logging.info(f"Collection {self.collection_name} exists")
        else:
           logging.info(f"Collection {self.collection_name} doesn't exist")
           result = self.database.create_collection(self.collection_name)
           logging.info(result)
        self.database.command("collMod", self.collection_name, validator=self.validator)
        self.collection = self.database.heatmaps
        self.exists = True

    def insert_one(self, obj_dict):
        if not self.exists:
            self._create_collection_if_not_exists()

        logging.info(f"Inserting guild object into the {self.collection_name} collection.")
        return self.collection.insert_one(obj_dict)

    def get_one(self):
        return self.database[self.collection_name].find_one()

    def get_all(self):
        return self.database[self.collection_name].find()

    def get_last_date(self):
        try:
            date_str = self.database[self.collection_name].find().sort([("date", pymongo.DESCENDING)]).limit(1)[0]["date"]

            #Parsing the time and timezone
            date_str = date_str.split(" GMT")
            date_str[1] = "GMT"+date_str[1]
            date_str[1] = date_str[1].split(" ")[0].replace("GMT","")
            zone = [date_str[1][0:3], date_str[1][3::]]
            zone_hrs = int(zone[0])
            zone_min = int(zone[1])
            date_obj = datetime.strptime(date_str[0], "%a %b %d %Y %H:%M:%S").replace(
                tzinfo=timezone(timedelta(hours=zone_hrs, minutes=zone_min))
            )
            return date_obj
        except Exception():
            print("No database entry with valid field 'date' found")
            return None
