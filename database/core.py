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

    def shutdown_db_client(self):
        self.client.close()
        print("Disconnected from the MongoDB database.")

    def get_db(self):
        return self.database