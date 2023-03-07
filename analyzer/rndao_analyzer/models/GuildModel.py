#!/usr/bin/env python3
import logging

from typing import TypedDict
from models.BaseModel import BaseModel

class GuildModel(BaseModel):
    def __init__(self, database=None):
        if database is None:
            logging.exception("Database does not exist.")
            raise Exception("Database should not be None")
        super().__init__(
            collection_name="guild",
            database=database)
        self.validator = {
            "$jsonSchema" :{
                "bsonType": "object",
                "required" : ["guildId","user"],
                "properties":{
                    "guildId":{
                        "bsonType": "string",
                    },
                    "user":{
                        "bsonType": "objectId",
                    },
                    "name":{
                       "bsonType":"string"
                    },
                    "selectedChannels": {
                        "bsonType":"array",
                        "items":{
                            "properties":{
                                "channelId":{
                                    "bsonType":"string"
                                },
                                "channelName":{
                                    "bsonType":"string"
                                }
                            }
                        }
                    },
                    "period":{
                        "bsonType":"date"
                    }
                }
            }
        }
