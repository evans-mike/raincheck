import requests
import dateutil.parser
from dotenv import dotenv_values
from openai import OpenAI
import datetime

config = dotenv_values(".env")

openai_client = OpenAI(
    api_key=config["OPENAI_API_KEY"],
)


class Forecast:

    def __init__(self, event):
        self.validate_event()
        self.place = event.place
        self.time = event.time
        self.get_hourly_forecast()
        self.summarize_forecast()

    def validate_event(self):
        if not hasattr(self, "place"):
            raise ValueError("Event object missing place")
        if not hasattr(self, "time"):
            raise ValueError("Event object missing time")

    def get_forecast(self):
        r = requests.get(
            f"https://api.weather.gov/gridpoints/{self.place.gridId}/{self.place.gridX},{self.place.gridY}/forecast/hourly"
        )
        r.raise_for_status()
        self.forecast["raw"] = r.json()["properties"]["periods"]

    def filter_forecast(self) -> dict:

        event_start_time = dateutil.parser.parse(self.time.startDateTime)
        event_end_time = dateutil.parser.parse(self.time.endDateTime)

        forecast_periods = []
        for period_forecast in self.forecast["raw"]:
            period_start = dateutil.parser.parse(period_forecast["startTime"])
            period_end = dateutil.parser.parse(period_forecast["endTime"])

            if event_start_time >= period_start and event_end_time <= period_end:
                forecast_periods.append(period_forecast)

        self.forecast = {}
        self.forecast["raw_filtered"] = forecast_periods

    def summarize_forecast(self):
        summary = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=350,
            prompt="Summarize the future hour-by-hour weather forecast in casual language addressing second person singular under 350 characters:",
            messages=[
                {
                    "role": "function",
                    "name": "summarize_forecast",
                    "content": f"Summarize the weather forecast in casual language addressing second person singular under 250 characters: {self.forecast['raw_filtered'], self.time}",
                }
            ],
        )
        self.forecast["chatgpt_summary"] = summary.choices[0].message

    def forecastable(self):

        if dateutil.parser.parse(
            self.time.startDateTime
        ) > datetime.datetime.now() and dateutil.parser.parse(
            self.time.startDateTime
        ) > (
            datetime.datetime.now() + datetime.timedelta(days=7)
        ):
            return False
        return True

    def main_get_forecast(self):

        if self.forecastable():
            self.get_forecast()
            self.filter_forecast()
            self.summarize_forecast()
