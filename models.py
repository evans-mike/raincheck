import uuid
from typing import Optional
from pydantic import BaseModel, Field
import urllib.parse
from functools import lru_cache 
import dateutil.parser
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

class User(BaseModel):
    username: str
    # email: str | None = None
    # full_name: str | None = None
    # disabled: bool | None = None



class Time(BaseModel):
    startDateTime: str = Field(...)
    # endDateTime: Optional[str] = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "startDateTime": "2023-12-11T06:00:00-05:00",
                "endDateTime": "..."
            }
        }


class Place(BaseModel):
    address: str = Field(...)
    # lat: Optional[float] = Field(...)
    # lon: Optional[float] = Field(...)
    # gridId: Optional[str] = Field(...)
    # gridX: Optional[int] = Field(...)
    # gridY: Optional[int] = Field(...)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
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