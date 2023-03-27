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
                    "lastDate": {
                        "bsonType": "date",
                    },
                    "activeAccounts": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "joinedAccounts": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "connectedAccounts": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
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

