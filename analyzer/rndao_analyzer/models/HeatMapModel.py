#!/usr/bin/env python3
import logging
import pymongo

from typing import TypedDict
from datetime import datetime, timezone, timedelta
from models.BaseModel import BaseModel

class HeatMapModel(BaseModel):
    def __init__(self, database=None):
        if database is None:
            logging.exception("Database does not exist.")
            raise Exception("Database should not be None")
        super().__init__(
            collection_name="heatmaps",
            database=database)
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




    def get_last_date(self):
        """
        Gets the date of the last document
        """
        try:
            date_str = self.database[self.collection_name].find().sort([("date", pymongo.DESCENDING)]).limit(1)[0]["date"]
            return date_str
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
        except Exception("No database entry with valid field found"):
            return None
