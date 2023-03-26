#!/usr/bin/env python3
import logging

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
