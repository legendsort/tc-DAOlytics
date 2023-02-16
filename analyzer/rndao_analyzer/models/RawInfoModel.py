#!/usr/bin/env python3
import logging
import pymongo

from typing import TypedDict
from datetime import datetime, timedelta
from models.BaseModel import BaseModel

class RawInfoModel(BaseModel):
    def __init__(self, database=None):
        if database is None:
            logging.info("Database does not exist.")
            raise Exception("Database should not be None")
        super().__init__(
            collection_name="rawinfos",
            database=database)
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
                    "datetime":{
                        "bsonType": "string",
                    },
                    "channelId":{
                        "bsonType": "string",
                    }
                }
            }
        }



    def get_first_date(self):
        """
        Get's the date of the first document in the collection
        For determining the analysis date ranges
        This is RawInfo specific method
        """
        all_entries = self.database[self.collection_name].find()#.sort([("created_at", pymongo.ASCENDING)]).limit(1)[0]["created_at"]
        valid_entries = [x for x in all_entries if "datetime" in x.keys()]

        if len(valid_entries) == 0:
            raise Exception("RawInfo collection has no entries with 'datetime' value")

        sorted_entries = sorted(valid_entries, key=lambda t: int(t["datetime"].replace("-","")))

        date_str = sorted_entries[0]["datetime"]
        date_obj = datetime.strptime(date_str[0], "%Y-%m-%d")

        return date_obj

    def count(self):
        """
        Returns the number of entries in this collection
        """
        return self.database[self.collection_name].count_documents({})

    def get_day_entries(self, day):
        """
        Gets the list of entries for the stated day
        This is RawInfo specific method
        """
        start_day = day.replace(hour=0, minute=0, second=0)
        end_day = start_day + timedelta(days=1)

        logging.info(f"Fetching the documents {self.database.name} | {self.collection_name}: {start_day} -> {end_day}")

        date_str = day.strftime("%Y-%m-%d")

        entries = self.database[self.collection_name].find(
            {'datetime': date_str})
        return list(entries)
