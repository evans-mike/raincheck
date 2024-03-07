from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, model_validator
import dateutil.parser
import requests
from dotenv import dotenv_values
import datetime
from bson.objectid import ObjectId
from openai import OpenAI
from tools.place_utilities import (
    _get_lat_lon_for_address_here,
    _get_gridpoints_by_lat_lon,
)

config = dotenv_values(".env")

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

    @model_validator(mode="after")
    def validate_start_end_times(self):
        if self.endDateTime and dateutil.parser.parse(
            self.startDateTime
        ) >= dateutil.parser.parse(self.endDateTime):
            raise ValueError("The startDateTime must be before the endDateTime.")
        return self

    @model_validator(mode="after")
    def validate_future_start_time(self):
        if dateutil.parser.parse(self.startDateTime) <= datetime.datetime.now(
            datetime.timezone(datetime.timedelta(-1, 68400), "EST")
        ):
            raise ValueError("The startDateTime must be in the future.")
        return self


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

    # def get_forecast_more_than_7_day(self):
    #     """
    #     If the event start time is beyond the last forecast period, return a message that the event is saved but the forecast is not available yet.
    #     """
    #     if dateutil.parser.parse(self.time.startDateTime) > (
    #         datetime.datetime.now() + datetime.timedelta(days=7)
    #     ):
    #         self.forecast = {
    #             "message": "The event is saved but the forecast is not available yet."
    #         }

    # def get_forecast_4_to_7_day(self):
    #     """
    #     If the event start time is within 96 hours to 7 days from now, return the full day forecast for the event day from f"https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast" and include the isDaytime==True and isDaytime==False periods in the forecast to describe the weather for the event day.
    #     """
    #     if (
    #         datetime.datetime.now() + datetime.timedelta(hours=96)
    #     ) < dateutil.parser.parse(self.time.startDateTime) and dateutil.parser.parse(self.time.startDateTime) > (
    #         datetime.datetime.now() + datetime.timedelta(days=7)
    #     ):
    #         r = requests.get(
    #             f"https://api.weather.gov/gridpoints/{self.place.gridId}/{self.place.gridX},{self.place.gridY}/forecast"
    #         )
    #         r.raise_for_status()
    #         self.forecast = []
    #         forecast = r.json()["properties"]["periods"]
    #         event_time = dateutil.parser.parse(self.time.startDateTime)
    #         for period_forecast in forecast:
    #             start_time = dateutil.parser.parse(period_forecast["startTime"])
    #             end_time = dateutil.parser.parse(period_forecast["endTime"])
    #             if event_time >= start_time and event_time <= end_time:
    #                 self.forecast.append(period_forecast)

    # def get_forecast_0_to_3_day(self):
    #     """
    #     If the event start time is within 0-96 hours from now, return the hourly forecast for the event day from f"https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast/hourly" and return the specific periods within the event start and end times. Summary should breakdown the hourly forecast for each hour within the event start and end times.
    #     """

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
                            "startDateTime": "2024-03-07T12:00:00-05:00",
                            "endDateTime": "2024-03-08T13:00:00-05:00",
                        },
                        "place": {"address": "123 Main St, Louisville, KY 40202"},
                    }
                ],
            }
        }
