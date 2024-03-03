from pydantic import BaseModel, Field, EmailStr
import urllib.parse
from functools import lru_cache
import dateutil.parser
from dotenv import dotenv_values
from bson.objectid import ObjectId
from datetime import datetime, timedelta, timezone
import requests
from typing import Optional, List
from bson import ObjectId

config = dotenv_values(".env")


"""
"subscriptions": [
    {
        "_id": "65dfa4bf6053318daf2d53f9",
        "subscriber": {
            "phone": "555-555-5555",
            "email": "",
            "alert_texts": True,
            "alert_emails": False
        },
        "events": [
            {
                "_id": "65dfa4bf6053318daf2d53f7",
                "time": {
                    "startDateTime": "2024-03-01T12:00:00-05:00",
                    "endDateTime": "2024-03-01T13:00:00-05:00"
                },
                "place": {
                    "address": "123 Main St, Louisville, KY 40202",
                    "lat": 38.2542,
                    "lon": 85.7594,
                    "gridId": "LMK",
                    "gridX": 84,
                    "gridY": 86
                },
                "forecast": {
                    "number": 1,
                    "name": "This is the forecast of an event.",
                    "startTime": "2024-03-01T12:00:00-05:00",
                    "endTime": "2024-03-01T13:00:00-05:00",
                    "isDaytime": True,
                    "temperature": 60,
                    "temperatureUnit": "F",
                    "windSpeed": "5 mph",
                    "windDirection": "SW",
                    "icon": "https://api.weather.gov/icons/land/day/sct?size=small",
                    "shortForecast": "Sunny",
                    "detailedForecast": "This is the detailed forecast of an event."
                }
            },
            {
                "_id": "65dfa4bf6053318daf2d53f8",
                "time": {
                    "startDateTime": "2024-03-01T12:00:00-05:00",
                    "endDateTime": "2024-03-01T13:00:00-05:00"
                },
                "place": {
                    "address": "123 Main St, Louisville, KY 40202",
                    "lat": 38.2542,
                    "lon": 85.7594,
                    "gridId": "LMK",
                    "gridX": 84,
                    "gridY": 86
                },
                "forecast": {
                    "number": 1,
                    "name": "This is the forecast of an event.",
                    "startTime": "2024-03-01T12:00:00-05:00",
                    "endTime": "2024-03-01T13:00:00-05:00",
                    "isDaytime": True,
                    "temperature": 60,
                    "temperatureUnit": "F",
                    "windSpeed": "5 mph",
                    "windDirection": "SW",
                    "icon": "https://api.weather.gov/icons/land/day/sct?size=small",
                    "shortForecast": "Sunny",
                    "detailedForecast": "This is the detailed forecast of an event."
                }
            }
        ]
    }
]
"""


class Subscriber(BaseModel):
    phone: str = "555-555-5555"
    email: Optional[EmailStr] = None
    alert_texts: Optional[bool] = Field(
        default=True,
        metadata=dict(
            title="This is whether the subscriber wants to receive text messages.",
            description="This is not requried.",
        ),
    )
    alert_emails: Optional[bool] = Field(
        default=False,
        metadata=dict(
            title="This is whether the subscriber wants to receive emails.",
            description="This is not requried.",
        ),
    )

    class Config:
        title = "Subscriber"
        description = "This is a subscriber."
        json_schema_extra = {
            "example": {
                "phone": "555-555-5555"
            }
        }


class Time(BaseModel):
    startDateTime: str = (
        datetime.now(timezone(timedelta(hours=-5), "EST")) + timedelta(days=1)
    ).isoformat()
    endDateTime: Optional[str] = (
        datetime.now(timezone(timedelta(hours=-5), "EST")) + timedelta(days=2)
    ).isoformat()

    class Config:
        title = "Time"
        description = "This is a time."
        json_schema_extra = {
            "example": {
                "startDateTime": "2024-03-01T12:00:00-05:00",
                "endDateTime": "2024-03-01T13:00:00-05:00",
            }
        }

    def validate_start_end_times(self):
        if dateutil.parser.parse(self.startDateTime) >= dateutil.parser.parse(
            self.endDateTime
        ):
            raise ValueError("The startDateTime must be before the endDateTime.")

    def validate_future_start_time(self):
        if dateutil.parser.parse(self.startDateTime) <= datetime.now(
            timezone(timedelta(-1, 68400), "EST")
        ):
            raise ValueError("The startDateTime must be in the future.")

    def model_post_init(self, __context):
        self.validate_start_end_times()
        self.validate_future_start_time()


class Place(BaseModel):
    address: str = Field(
        default="123 W Main St, Louisville, KY 40202",
        title="This is the address of a Place of an event.",
    )
    lat: Optional[float] = Field(
        default=None,
        title="This is the latitude of a Place of an event.",
        description="This is not required.",
    )
    lon: Optional[float] = Field(
        default=None,
        title="This is the longitude of a Place of an event.",
        description="This is not required.",
    )
    gridId: Optional[str] = Field(
        default=None,
        title="This is the gridId of a Place of an event.",
        description="This is not required.",
    )
    gridX: Optional[int] = Field(
        default=None,
        title="This is the gridX of a Place of an event.",
        description="This is not required.",
    )
    gridY: Optional[int] = Field(
        default=None,
        title="This is the gridY of a Place of an event.",
        description="This is not required.",
    )

    def get_lat_lon_for_address(self):

        address_encoded = urllib.parse.quote_plus(self.address)

        r = requests.get(
            f'https://maps.googleapis.com/maps/api/geocode/json?address={address_encoded}&key={config["GOOGLE_API_KEY"]}'
        )
        r.raise_for_status()
        if r.json()["status"] == "ZERO_RESULTS":
            raise ValueError("The address provided returned no results.")
        self.lat = r.json()["results"][0]["geometry"]["location"]["lat"]
        self.lon = r.json()["results"][0]["geometry"]["location"]["lng"]

    def get_gridpoints_by_lat_lon(self):
        r = requests.get(f"https://api.weather.gov/points/{self.lat},{self.lon}")
        r.raise_for_status()
        self.gridId = r.json()["properties"]["gridId"]
        self.gridX = r.json()["properties"]["gridX"]
        self.gridY = r.json()["properties"]["gridY"]

    def model_post_init(self, __context):
        self.get_lat_lon_for_address()
        self.get_gridpoints_by_lat_lon()

    class Config:
        title = "Place"
        description = "This is a place."
        json_schema_extra = {
            "example": {
                "address": "123 Main St, Louisville, KY 40202",
                "lat": 38.2542,
                "lon": 85.7594,
                "gridId": "LMK",
                "gridX": 84,
                "gridY": 86,
            }
        }


# @dataclasses.dataclass
# class Notification(Subscriber):

#     subscribed_texts: Optional[bool] = dataclasses.field(
#         default=True,
#         metadata=dict(title='This is whether the subscriber wants to receive text messages.', description='This is not requried.')
#     )
#     subscribed_emails: Optional[bool] = dataclasses.field(
#         default=False,
#         metadata=dict(title='This is whether the subscriber wants to receive emails.', description='This is not requried.')
#     )

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "phone": "555-555-5555",
#                 "email": "someperson@raincheck.com",
#                 "subscribed_texts": True,
#                 "subscribed_emails": False
#             }
#         }


class Event(BaseModel):
    time: Time
    place: Place
    forecast: Optional[object] = Field(
        default=None, title="This is the forecast of an event."
    )
    event_id: Optional[str] = Field(
        alias="_event_id", default=str(ObjectId()), title="This is the id of the event."
    )

    def get_event_forecast(self) -> dict:
        r = requests.get(
            f"https://api.weather.gov/gridpoints/{self.place.gridId}/{self.place.gridX},{self.place.gridY}/forecast/hourly"
        )
        r.raise_for_status()

        forecast = r.json()["properties"]["periods"]

        event_time = dateutil.parser.parse(self.time.startDateTime)

        for period_forecast in forecast:
            start_time = dateutil.parser.parse(period_forecast["startTime"])
            end_time = dateutil.parser.parse(period_forecast["endTime"])

            if event_time >= start_time and event_time <= end_time:
                break

        self.forecast = period_forecast

    def model_post_init(self, __context):
        self.get_event_forecast()

    class Config:
        populate_by_alias = True
        json_schema_extra = {
            "example": {
                "time": {
                    "startDateTime": "2024-03-01T12:00:00-05:00",
                    "endDateTime": "2024-03-01T13:00:00-05:00"
                },
                "place": {
                    "address": "123 Main St, Louisville, KY 40202"
                },
            }
        }


class Subscription(BaseModel):
    subscriber: Subscriber
    events: List[Event]
    event_id: Optional[str] = Field(
        alias="_event_id", default=None, title="This is the id of the subscription."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "subscriber": {
                    "phone": "555-555-5555"
                },
                "events": [
                    {
                        "time": {
                            "startDateTime": "2024-03-01T12:00:00-05:00",
                            "endDateTime": "2024-03-01T13:00:00-05:00"
                        },
                        "place": {
                            "address": "123 Main St, Louisville, KY 40202"
                        }
                    }
                ]
            }
        }
