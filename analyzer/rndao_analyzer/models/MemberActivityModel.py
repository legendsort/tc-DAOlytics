#!/usr/bin/env python3
import logging
import pymongo
import datetime

from models.BaseModel import BaseModel


class MemberActivityModel(BaseModel):
    def __init__(self, database=None):
        if database is None:
            logging.exception("Database does not exist.")
            raise Exception("Database should not be None")
        super().__init__(
            collection_name="memberactivities",
            database=database)
        self.validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {
                    "first_end_date": {
                        "bsonType": "date",
                    },
                    "all_active": {
                        "bsonType": "object",
                    },
                    "all_consistent": {
                        "bsonType": "object",
                    },
                    "all_vital": {
                        "bsonType": "object",
                    },
                    "all_connected": {
                        "bsonType": "object",
                    },
                    "all_paused": {
                        "bsonType": "object",
                    },
                    "all_new_disengaged": {
                        "bsonType": "object",
                    },
                    "all_disengaged": {
                        "bsonType": "object",
                    },
                    "all_unpaused": {
                        "bsonType": "object",
                    },
                    "all_returned": {
                        "bsonType": "object",
                    },
                    "all_new_active": {
                        "bsonType": "object",
                    },
                    "all_still_active": {
                        "bsonType": "object",
                    },
                    "all_dropped": {
                        "bsonType": "object",
                    },
                    "all_joined": {
                        "bsonType": "object",
                    },
                    "all_disengaged_were_newly_active": {
                        "bsonType": "object",
                    },
                    "all_disengaged_were_consistenly_active": {
                        "bsonType": "object",
                    },
                    "all_disengaged_were_vital": {
                        "bsonType": "object",
                    },
                }
            }
        }
    def get_last_date(self):
        """
        Gets the date of the last document
        """
        try:
            date_str = self.database[self.collection_name].find().sort(
                [("first_end_date", pymongo.DESCENDING)]).limit(1)[0]["first_end_date"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj
        except Exception as e:
            print(e)
            return None

