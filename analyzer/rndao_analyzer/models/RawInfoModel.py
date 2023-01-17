#!/usr/bin/env python3
import logging
from typing import TypedDict

class RawInfoModel():
    def __init__(self, database=None):
        if database is None:
            logging.info("Database does not exist.")
            raise Exception("Database should not be None")
        self.database = database
        self.collection_name = "rawInfo"
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

    def _create_collection_if_not_exists(self):
        logging.info(f"Check if collection {self.collection_name} exists in database")
        if self.collection_name in self.database.list_collection_names():
           logging.info(f"Collection {self.collection_name} exists")
        else:
           logging.info(f"Collection {self.collection_name} doesn't exist")
           result = self.database.create_collection(self.collection_name)
           logging.info(result)
        self.database.command("collMod", self.collection_name, validator=self.validator)
        self.collection = self.database.rawInfo
        self.exists = True

    def insert_one(self, obj_dict):
        if not self.exists:
            self._create_collection_if_not_exists()

        print("INSERTING")
        logging.info(f"Inserting guild object into the {self.collection_name} collection.")
        return self.collection.insert_one(obj_dict)