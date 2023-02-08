#!/usr/bin/env python3



class BaseModel():
    """
    BaseModel description
    All integrated models inherit from this object
    """
    def __init__(self, collection_name, database):
        self.collection_name = collection_name
        self.database = database
        self.exists = False

    def collection_exists(self):
        """
        Collection presence test
        returns True if collection with this name exists in the
        database
        """
        if self.collection_name in self.database.list_collection_names():
            return True
        else:
            return False

    def insert_one(self, obj_dict, create=False):
        """
        Inserts one document into the defined collection
        If create is True than a new collection is created
        """
        if create:
            if not self.exists:
                self._create_collection_if_not_else()

        if not self.exists:
            logging.info(f"Inserting guild object into the {self.collection_name} collection failed: Collection does not exist")
            return

        logging.info(f"Inserting guild object into the {self.collection_name} collection.")
        return self.collection.insert_one(obj_dict)

    def _create_collection_if_not_exists(self):
        """
        Creates the collection with specified name if it does not exist
        """
        logging.info(f"Check if collection {self.collection_name} exists in database")
        if self.collection_name in self.database.list_collection_names():
           logging.info(f"Collection {self.collection_name} exists")
        else:
           logging.info(f"Collection {self.collection_name} doesn't exist")
           result = self.database.create_collection(self.collection_name)
           logging.info(result)
        self.database.command("collMod", self.collection_name, validator=self.validator)
        self.collection = self.database[self.collection_name]
        self.exists = True

    def get_one(self):
        """
        Gets one documents from the database,
        For testing purposes, no filtering is implemented.
        """
        return self.database[self.collection_name].find_one()

    def get_all(self):
        """
        Gets all documents from the database
        """

        return self.database[self.collection_name].find()
