#!/usr/bin/env python3
import logging
from typing import TypedDict


class UserModel():
    def __init__(self, database=None):
        if database is None:
            logging.info("Database does not exist.")
            raise Exception("Database should not be None")
        self.database = database
        self.collection_name = "user"
        self.exists = False
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


    def _create_collection_if_not_exists(self):
        logging.info(f"Check if collection {self.collection_name} exists in database")
        if self.collection_name in self.database.list_collection_names():
           logging.info(f"Collection {self.collection_name} exists")
        else:
           logging.info(f"Collection {self.collection_name} doesnt exist")
           result = self.database.create_collection(self.collection_name)
           logging.info(result)
        self.collection = self.database.user
        self.database.command("collMod", self.collection_name, validator=self.validator)
        self.exists = True

    def insert_one(self, obj_dict):
        if not self.exists:
            print("Not existing")
            self._create_collection_if_not_exists()
        logging.info(f"Inserting user entry into the {self.collection_name} collection.")
        return self.collection.insert_one(obj_dict)
