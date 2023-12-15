
import json
from fastapi import FastAPI
from dotenv import dotenv_values
import redis
from pymongo import MongoClient
from contextlib import asynccontextmanager

from routes import router


# def write_local_file(filename, dictionary):
    
#     if isinstance(dictionary, dict):
#         content = json.dumps(dictionary, indent=4)
#     else:
#         content = str(dictionary)

#     with open(f"{filename}.json", "w") as outfile:
#         outfile.write(content)





def get_whole_forecast(gridId, gridX, gridY) -> dict:
    r = requests.get(f'https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast')

    write_local_file("forecast", r.json())

    forecast = r.json()['properties']['periods']

    return forecast


def get_forecast_for_period(whole_forecast: dict, event_time) -> dict:

    
    event_time = dateutil.parser.parse(event_time)
    for period_forecast in whole_forecast:
        start_time = dateutil.parser.parse(period_forecast['startTime'])
        end_time = dateutil.parser.parse(period_forecast['endTime'])

        if event_time >= start_time and event_time <= end_time:
            write_local_file("period_forecast", period_forecast)

    return period_forecast


config = dotenv_values(".env")

def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print("Connected to the MongoDB database!")

def shutdown_db_client():
    app.mongodb_client.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    #(deprecated) @app.on_event("startup")
    startup_db_client()
    yield
    # (deprecated) @app.on_event("shutdown")
    shutdown_db_client()


app = FastAPI(lifespan=lifespan)

app.include_router(router, tags=["endpoints"], prefix="")

# if __name__ == '__main__':