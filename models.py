import uuid
from typing import Optional
from pydantic import BaseModel, Field
import urllib.parse
from functools import lru_cache 
import dateutil.parser
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")


class Time(BaseModel):
    startDateTime: str = Field(...)
    endDateTime: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "eventId": "166de609-b04a-4b30-b46c-32537c7f1f6f",
                "startDateTime": "2023-12-11T06:00:00-05:00",
                "endDateTime": "..."
            }
        }


class Place(BaseModel):
    address: str = Field(...)
    lat: float = Field(...)
    lon: float = Field(...)
    gridId: str = Field(...)
    gridX: int = Field(...)
    gridY: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "eventId": "166de609-b04a-4b30-b46c-32537c7f1f6f",
                "address": "123 E Main StLouisville, KY 40202",
                "lat": "...",
                "lon": "...",
                "gridId": "...",
                "gridX": "...",
                "gridY": "..."
            }
        }
    
    @lru_cache
    def get_lat_lon_for_address(address):
        
        address_encoded = urllib.parse.quote_plus(address)

        r = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address_encoded}&key={config["GOOGLE_API_KEY"]}')
        
        lat = r.json()['results'][0]['geometry']['location']['lat']
        lon = r.json()['results'][0]['geometry']['location']['lng']

        return lat, lon


    @lru_cache
    def get_gridpoints_by_lat_lon(lat, lon) -> str:
        r = requests.get(f'https://api.weather.gov/points/{lat},{lon}')
        
        gridId = r.json()['properties']['gridId']
        gridX = r.json()['properties']['gridX']
        gridY = r.json()['properties']['gridY']

        return gridId, gridX, gridY


class Subscriber(BaseModel):
    email: str = Field(...)
    phone: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6f",
                "eventId": "166de609-b04a-4b30-b46c-32537c7f1f6f",
                "email": "someperson@somedomain.com",
                "phone": "..."
            }
        }


class Forecast(BaseModel):

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6f"
            }
        }

    def get_whole_forecast(gridId, gridX, gridY) -> dict:
        r = requests.get(f'https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast')

        forecast = r.json()['properties']['periods']

        return forecast


    def get_forecast_for_period(whole_forecast: dict, event_time) -> dict:

    
        event_time = dateutil.parser.parse(event_time)
        for period_forecast in whole_forecast:
            start_time = dateutil.parser.parse(period_forecast['startTime'])
            end_time = dateutil.parser.parse(period_forecast['endTime'])

            if event_time >= start_time and event_time <= end_time:
                # condition met
                break

        return period_forecast


# TODO: add Notification model to extent Subscriber model

class Event(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
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
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "time": "{...}",
                "place": "{...}",
                "forecast": "{...}",
                "subscriber": "{...}"
            }
        }