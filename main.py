
from fastapi import FastAPI, Depends
from dotenv import dotenv_values
from pymongo import MongoClient
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from routes import router




# TODO: Authentication https://fastapi.tiangolo.com/tutorial/security/first-steps/

# TODO: Logger https://docs.python.org/3/howto/logging-cookbook.html

# if __name__ == '__main__':

config = dotenv_values(".env")

def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

def shutdown_db_client():
    app.mongodb_client.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_db_client()
    yield
    shutdown_db_client()


app = FastAPI(lifespan=lifespan)

app.include_router(router, tags=["endpoints"], prefix="")
