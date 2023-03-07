#!/usr/bin/env python3
import logging
from typing import TypedDict
from models.BaseModel import BaseModel

class UserModel(BaseModel):
    def __init__(self, database=None):
        if database is None:
            logging.exception("Database does not exist.")
            raise Exception("Database should not be None")
        super().__init__(
            collection_name="user",
            database=database)
        self.validator = {
            "$jsonSchema" :{
                "bsonType": "object",
                "required" : ["discordId", "email"],
                "properties":{
                    "discordId":{
                        "bsonType":"string",
                        "uniqueItems":True,
                    },
                    "email":{
                        "bsonType": "string",
                        "uniqueItems":True,
                    },
                    "verified":{
                        "bsonType":"bool"
                    },
                    "avatar":{
                        "bsonType":"string"
                    }
                }
            }
        }
