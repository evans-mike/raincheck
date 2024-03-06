from typing import Optional
from dotenv import dotenv_values
from pymongo import MongoClient
from contextlib import asynccontextmanager

config = dotenv_values(".env")


class NotFoundError(Exception):
    pass


class DB:

    def __init__(self):
        self.client = MongoClient(config["ATLAS_URI"])
        self.database = self.client[config["DB_NAME"]]
        self.get_or_create_collection()

    def shutdown_db_client(self):
        self.client.close()
        print("Disconnected from the MongoDB database.")

    def get_or_create_collection(self):
        if self.database.get_collection("subscriptions") == None:
            self.database.create_collection("subscriptions")
            self.database.subscriptions.create_index("subscriber.phone", unique=True)
            print("Database created.")
        return self.database.subscriptions

    def __post_init__(self):
        self.database = self.client[config["DB_NAME"]]
        self.get_db()
