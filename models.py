import uuid
from typing import Optional
import dataclasses
from pydantic import BaseModel, Field, dataclass
import urllib.parse
from functools import lru_cache 
import dateutil.parser
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

@dataclass
class Time:
    startDateTime: str = dataclasses.field(
        default=None,
        metadata=dict(title='This is the startDateTime of an event.')
    )
    endDateTime: Optional[str] = dataclasses.field(
        default=None,
        metadata=dict(title='This is the endDateTime of an event.', description='This is not requried.')
    )

@dataclass
class Place:
    address: str
    lat: Optional[float]
    lon: Optional[float]
    gridId: Optional[str]
    gridX: Optional[int]
    gridY: Optional[int]

    @lru_cache
    def get_lat_lon_for_address(self):
        
        address_encoded = urllib.parse.quote_plus(self.address)

        r = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address_encoded}&key={config["GOOGLE_API_KEY"]}')
        # if HTTP 200
        self.lat = r.json()['results'][0]['geometry']['location']['lat']
        self.lon = r.json()['results'][0]['geometry']['location']['lng']

        # return self.lat, self.lon


    @lru_cache
    def get_gridpoints_by_lat_lon(self) -> str:
        r = requests.get(f'https://api.weather.gov/points/{self.lat},{self.lon}')
        # if HTTP 200
        self.gridId = r.json()['properties']['gridId']
        self.gridX = r.json()['properties']['gridX']
        self.gridY = r.json()['properties']['gridY']

        # return self.gridId, self.gridX, self.gridY


class Subscriber(BaseModel):
    # email: Optional[str] = Field(...)
    phone: str = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "email": "someperson@somedomain.com",
                "phone": "..."
            }
        }


class Forecast(BaseModel):

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
            }
        }

    # def get_whole_forecast(gridId, gridX, gridY) -> dict:
    #     r = requests.get(f'https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast')

    #     forecast = r.json()['properties']['periods']

    #     return forecast


    def get_forecast_for_time_and_place(gridId, gridX, gridY, event_time) -> dict:

        r = requests.get(f'https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast/hourly')

        forecast = r.json()['properties']['periods']
    
        event_time = dateutil.parser.parse(event_time)
        for period_forecast in forecast:
            start_time = dateutil.parser.parse(period_forecast['startTime'])
            end_time = dateutil.parser.parse(period_forecast['endTime'])

            if event_time >= start_time and event_time <= end_time:
                # condition met
                break

        return period_forecast


# TODO: add Notification model to extent Subscriber model

class Event(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias="_id")
    time: Time
    place: Place

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e"
            }
        }


class EventUpdate(Event):
    time: Time
    place: Place
    subscriber: Subscriber
    forecast: Forecast
    

    class Config:
        json_schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "time": "{...}",
                "place": "{...}",
                "forecast": "{...}",
                "subscriber": "{...}"
            }
        }