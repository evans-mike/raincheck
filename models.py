from typing import Optional
import dataclasses
from pydantic.dataclasses import dataclass
import urllib.parse
from functools import lru_cache
import dateutil.parser
import requests
from dotenv import dotenv_values
import datetime

config = dotenv_values(".env")


"""
"subcription": {
    "_id": "65dfa4bf6053318daf2d53f5",
    "subscriber": {
        "_id": "65dfa4bf6053318daf2d53f6",
        "phone": "555-555-5555",
        "email": ""
    },
    "events": [
        {
            "_id": "65dfa4bf6053318daf2d53f7",
            "time": {
                "startDateTime": "2024-03-01T12:00:00-05:00",
                "endDateTime": "2024-03-01T13:00:00-05:00"
            },
            "place": {
                "address": "123 Main St, Louisville, KY 40202"
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
                "address": "123 Main St, Louisville, KY 40202"
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

"""


@dataclass
class SubscriberDetails:
    phone: str = dataclasses.field(
        default="555-555-5555",
        metadata=dict(title="This is the phone number of a Subscriber."),
    )
    email: Optional[str] = dataclasses.field(
        default=None,
        metadata=dict(
            title="This is the email of a Subscriber.",
            description="This is not required.",
        ),
    )


@dataclass
class Subscriber:
    subscriber: SubscriberDetails


@dataclass
class Time:
    startDateTime: str = dataclasses.field(
        default=datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=-5), "EST")
        )
        + datetime.timedelta(days=1),
        metadata=dict(title="This is the startDateTime of an event."),
    )
    endDateTime: Optional[str] = dataclasses.field(
        default=datetime.datetime.now(
            datetime.timezone(datetime.timedelta(hours=-5), "EST")
        )
        + datetime.timedelta(days=2),
        metadata=dict(
            title="This is the endDateTime of an event.",
            description="This is not required.",
        ),
    )

    def validate_start_end_times(self):
        if dateutil.parser.parse(self.startDateTime) >= dateutil.parser.parse(
            self.endDateTime
        ):
            raise ValueError("The startDateTime must be before the endDateTime.")

    def validate_future_start_time(self):
        if dateutil.parser.parse(self.startDateTime) <= datetime.datetime.now(
            datetime.timezone(datetime.timedelta(-1, 68400), "EST")
        ):
            raise ValueError("The startDateTime must be in the future.")

    def __post_init__(self):
        self.validate_start_end_times()
        self.validate_future_start_time()


@dataclass
class Place:
    address: str = dataclasses.field(
        default="123 W Main St, Louisville, KY 40202",
        metadata=dict(title="This is the address of a Place of an event."),
    )
    lat: Optional[float] = dataclasses.field(
        default=None,
        metadata=dict(
            title="This is the latitude of a Place of an event.",
            description="This is not required.",
        ),
    )
    lon: Optional[float] = dataclasses.field(
        default=None,
        metadata=dict(
            title="This is the longitude of a Place of an event.",
            description="This is not requried.",
        ),
    )
    gridId: Optional[str] = dataclasses.field(
        default=None,
        metadata=dict(
            title="This is the gridId of a Place of an event.",
            description="This is not requried.",
        ),
    )
    gridX: Optional[int] = dataclasses.field(
        default=None,
        metadata=dict(
            title="This is the gridX of a Place of an event.",
            description="This is not requried.",
        ),
    )
    gridY: Optional[int] = dataclasses.field(
        default=None,
        metadata=dict(
            title="This is the gridY of a Place of an event.",
            description="This is not required.",
        ),
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

    def __post_init__(self):
        self.get_lat_lon_for_address()
        self.get_gridpoints_by_lat_lon()


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


@dataclass
class Event:
    time: Time
    place: Place
    forecast: Optional[object] = dataclasses.field(
        default=None, metadata=dict(title="This is the forecast of an event.")
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "time": {
                    "startDateTime": "2024-03-01T12:00:00-05:00",
                    "endDateTime": "2024-03-01T13:00:00-05:00",
                },
                "place": {"address": "123 Main St, Louisville, KY 40202"},
            }
        }

    def get_event_forecast(self) -> dict:  # TODO: break this into smaller methods

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

    def __post_init__(self):
        self.get_event_forecast()


# @dataclasses.dataclass
# class EventUpdate(Event): # WIP
#     time: Time
#     place: Place
#     forecast: Optional[object] = dataclasses.field(
#         default=None,
#         metadata=dict(title='This is the forecast of an event.')
#     )
#     subscriber: Subscriber

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
#                 "time": "{...}",
#                 "place": "{...}",
#                 "forecast": "{...}",
#                 "subscriber": "{...}"
#             }
#         }
