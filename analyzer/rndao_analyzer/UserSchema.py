#!/usr/bin/env python3
import logging
from typing import TypedDict


class UserModel():
    def __init__(self, database):
        if database is None:
            logging.info("Database does not exist.")
            raise Exception()
        self.database = database
        self.collection_name = "user"
        self.exists = False
        print("test")

    def _create_collection(self):
        validator = {
            "$jsonSchema" :{
                "bsonType": "object",
                "required" : ["discordId", "email"],
                "uniqueItems" : ["discordId", "email"],
                "properties":{
                    "discordId":{
                        "bsonType":"string",
                        "unique":True,
                    },
                    "email":{
                        "bsonType": "string",
                        "trim":"true",
                        "lowercase":"true",
                    },
                    "verified":{
                        "bsonType":"boolean"
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
        self.exists = True

    def insert_one(self, discordId, email, verified, avatar):
        if not self.exists:
            print("Not existing")
            self._create_collection_if_not_exists()
        logging.info(f"Inserting {discordId} into the {self.collection} collection.")
        obj_dict = {
            "discordId": discordId,
            "email": email,
            "verified": verified,
            "avatar":avatar
        }
        self.collection.insert_one(obj_dict)
