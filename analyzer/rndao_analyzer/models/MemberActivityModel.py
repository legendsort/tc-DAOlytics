#!/usr/bin/env python3
import logging
import pymongo
from datetime import datetime

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
                    "date": {
                        "bsonType": "date",
                    },
                    "all_active": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_consistent": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_vital": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_connected": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_paused": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_new_disengaged": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_disengaged": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_unpaused": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_returned": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_new_active": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_still_active": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_dropped": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_joined": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_disengaged_were_newly_active": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_disengaged_were_consistenly_active": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "string"
                        }
                    },
                    "all_disengaged_were_vital": {
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
                [("date", pymongo.DESCENDING)]).limit(1)[0]["date"]
            date_format = '%Y-%m-%dT%H:%M:%S'
            date_object = datetime.strptime(date_str, date_format)
            return date_object
        except Exception as e:
            print(e)
            return None

