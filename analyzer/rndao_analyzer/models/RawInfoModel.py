#!/usr/bin/env python3
import logging
from typing import TypedDict
import pymongo
from datetime import datetime, timedelta

class RawInfoModel():
    def __init__(self, database=None):
        if database is None:
            logging.info("Database does not exist.")
            raise Exception("Database should not be None")
        self.database = database
        self.collection_name = "rawinfos"
        self.exists = False
        self.validator = {
            "$jsonSchema" :{
                "bsonType": "object",
                "properties":{
                    "type":{
                        "bsonType":"string"
                    },
                    "author" :{
                        "bsonType":"string"
                    },
                    "content" :{
                        "bsonType":"string"
                    },
                    "user_Mentions":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"string"
                        }
                    },
                    "roles_Mentions":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"string"
                        }
                    },
                    "reactions":{
                        "bsonType":"array",
                        "items":{
                            "bsonType":"string"
                        }
                    },
                    "replied_User" :{
                        "bsonType":"string"
                    },
                    "reference_Message" :{
                        "bsonType":"int"
                    },
                    "created_at":{
                        "bsonType": "date",
                    },
                    "channelId":{
                        "bsonType": "string",
                    }
                }
            }
        }

    def is_present(self):
        print(self.database.list_collection_names())
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
        self.collection = self.database[self.collection_name]
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

    def get_first_date(self):
            all_entries = self.database[self.collection_name].find()#.sort([("created_at", pymongo.ASCENDING)]).limit(1)[0]["created_at"]
            valid_entries = [x for x in all_entries if "created_at" in x.keys()]
            if len(valid_entries) == 0:
                raise Exception("RawInfo collection has no entries with 'created_at' value")
            sorted_entries = sorted(valid_entries, key=lambda t: t["created_at"])
            return sorted_entries[0]["created_at"]

    def get_day_entries(self, day):
        start_day = day.replace(hour=0, minute=0, second=0)
        end_day = start_day + timedelta(days=1)

        print(f"{start_day} -> {end_day}")
        entries = self.database[self.collection_name].find(
            {'created_at':{'$gte':start_day, '$lt':end_day}})
        #if len(list(entries))>0:
        return list(entries)

    def test_get(self):
        test_day = datetime(2023,1,6,17)

        start_day = test_day.replace(hour=0, minute=0, second=0)
        end_day = start_day + timedelta(days=1)

        print(f"{start_day} -> {end_day}")
        print("_")
        entries = self.database[self.collection_name].find(
            {'created_at':{'$gte':start_day, '$lt':end_day}})
        print(list(entries))
