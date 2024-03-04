from typing import Optional
import dataclasses
from pydantic import BaseModel, Field, EmailStr
from pydantic.dataclasses import dataclass
import urllib.parse
from functools import lru_cache
import dateutil.parser
import requests
from dotenv import dotenv_values
import datetime

config = dotenv_values(".env")

from openai import OpenAI

openai_client = OpenAI(
    api_key=config["OPENAI_API_KEY"],
)

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
                    "raw": {
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
                    },
                    "chatgpt_chatgpt_summary": {
                        "content": "Expect showers and thunderstorms for your event with a high of 66°F and 83% chance of rain. Winds from the south at 10 mph. Stay dry and prepare for wet conditions!",
                        "role": "assistant",
                        "function_call": null,
                        "tool_calls": null
                    }
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
    phone: str = Field(
        default="555-555-5555",
        metadata=dict(title="This is the phone number of a Subscriber."),
    )
    email: Optional[EmailStr] = Field(
        default=None,
        metadata=dict(
            title="This is the email of a Subscriber.",
            description="This is not required.",
        ),
    )
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
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "phone": "555-555-5555",
            }
        }


class Time(BaseModel):
    startDateTime: str = Field(
        default=datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=-5), "EST")
        )
        + datetime.timedelta(days=1),
        metadata=dict(title="This is the startDateTime of an event."),
    )
    endDateTime: Optional[str] = Field(
        default=datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=-5), "EST")
        )
        + datetime.timedelta(days=2),
        metadata=dict(
            title="This is the endDateTime of an event.",
            description="This is not required.",
        ),
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {"example": {"startDateTime": "2024-03-01T12:00:00-05:00"}}

    def validate_start_end_times(self):
        if self.endDateTime and dateutil.parser.parse(
            self.startDateTime
        ) >= dateutil.parser.parse(self.endDateTime):
            raise ValueError("The startDateTime must be before the endDateTime.")

    def validate_future_start_time(self):
        if dateutil.parser.parse(self.startDateTime) <= datetime.datetime.now(
            datetime.timezone(datetime.timedelta(-1, 68400), "EST")
        ):
            raise ValueError("The startDateTime must be in the future.")

    def model_post_init(self, *args, **kwargs):
        self.validate_start_end_times()
        self.validate_future_start_time()


@lru_cache
def _get_lat_lon_for_address_google(address_str: str) -> tuple[float, float]:

    address_encoded = urllib.parse.quote_plus(address_str)

    r = requests.get(
        f'https://maps.googleapis.com/maps/api/geocode/json?address={address_encoded}&key={config["GOOGLE_API_KEY"]}'
    )
    r.raise_for_status()
    if r.json()["status"] == "ZERO_RESULTS":
        raise ValueError("The address provided returned no results.")
    lat = r.json()["results"][0]["geometry"]["location"]["lat"]
    lon = r.json()["results"][0]["geometry"]["location"]["lng"]

    return lat, lon


@lru_cache
def _get_lat_lon_for_address_here(address_str: str) -> tuple[float, float]:

    address_encoded = urllib.parse.quote_plus(address_str)

    r = requests.get(
        f'https://geocode.search.hereapi.com/v1/geocode?apiKey={config["HERE_API_KEY"]}&q={address_encoded}'
    )
    r.raise_for_status()
    if not r.json()["items"]:
        raise ValueError("The address provided returned no results.")

    lat = r.json()["items"][0]["position"]["lat"]
    lon = r.json()["items"][0]["position"]["lng"]

    return lat, lon


@lru_cache
def _get_gridpoints_by_lat_lon(lat: float, lon: float) -> tuple[str, int, int]:
    r = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
    r.raise_for_status()
    gridId = r.json()["properties"]["gridId"]
    gridX = r.json()["properties"]["gridX"]
    gridY = r.json()["properties"]["gridY"]

    return gridId, gridX, gridY


class Place(BaseModel):
    address: str = Field(
        default="123 W Main St, Louisville, KY 40202",
        metadata=dict(title="This is the address of a Place of an event."),
    )
    lat: Optional[float] = Field(
        default=None,
        metadata=dict(
            title="This is the latitude of a Place of an event.",
            description="This is not required.",
        ),
    )
    lon: Optional[float] = Field(
        default=None,
        metadata=dict(
            title="This is the longitude of a Place of an event.",
            description="This is not requried.",
        ),
    )
    gridId: Optional[str] = Field(
        default=None,
        metadata=dict(
            title="This is the gridId of a Place of an event.",
            description="This is not requried.",
        ),
    )
    gridX: Optional[int] = Field(
        default=None,
        metadata=dict(
            title="This is the gridX of a Place of an event.",
            description="This is not requried.",
        ),
    )
    gridY: Optional[int] = Field(
        default=None,
        metadata=dict(
            title="This is the gridY of a Place of an event.",
            description="This is not required.",
        ),
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {"address": "123 Main St, Louisville, KY 40202"}
        }

    def get_lat_lon_for_address(self):
        self.lat, self.lon = _get_lat_lon_for_address_here(self.address)

    def get_gridpoints_by_lat_lon(self):
        self.gridId, self.gridX, self.gridY = _get_gridpoints_by_lat_lon(
            self.lat, self.lon
        )

    def model_post_init(self, *args, **kwargs):
        self.get_lat_lon_for_address()
        self.get_gridpoints_by_lat_lon()


class Event(BaseModel):
    time: Time
    place: Place
    forecast: Optional[object] = Field(
        default=None, metadata=dict(title="This is the forecast of an event.")
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "time": {
                    "startDateTime": "2024-03-01T12:00:00-05:00",
                },
                "place": {"address": "123 Main St, Louisville, KY 40202"},
            }
        }

    def get_hourly_forecast(self) -> dict:  # TODO: break this into smaller methods

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

        self.forecast = {}
        self.forecast["raw"] = period_forecast

    def summarize_forecast(self):
        summary = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=250,
            messages=[
                {
                    "role": "function",
                    "name": "summarize_forecast",
                    "content": f"Summarize the weather forecast in casual language addressing second person singular under 250 characters: {self.forecast['raw'], self.time}",
                }
            ],
        )
        self.forecast["chatgpt_summary"] = summary.choices[0].message

    def model_post_init(self, *args, **kwargs):
        self.get_hourly_forecast()
        self.summarize_forecast()


class Subscription(BaseModel):
    subscriber: Subscriber
    events: list[Event]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "subscriber": {"phone": "555-555-5555"},
                "events": [
                    {
                        "time": {
                            "startDateTime": "2024-03-01T12:00:00-05:00",
                        },
                        "place": {"address": "123 Main St, Louisville, KY 40202"},
                    }
                ],
            }
        }
