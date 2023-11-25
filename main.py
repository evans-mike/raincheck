import requests
import json
import os
from dotenv import load_dotenv
import urllib.parse
from functools import lru_cache 
import redis
import dateutil.parser
import datetime


def write_local_file(filename, dictionary):
    
    if isinstance(dictionary, dict):
        content = json.dumps(dictionary, indent=4)
    else:
        content = str(dictionary)

    with open(f"{filename}.json", "w") as outfile:
        outfile.write(content)


@lru_cache
def get_lat_lon_for_address(address_string):
    
    address_encoded = urllib.parse.quote_plus(address_string)

    r = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address_encoded}&key={GOOGLE_API_KEY}')

    write_local_file("geocodes", r.json())
    
    lat = r.json()['results'][0]['geometry']['location']['lat']
    lon = r.json()['results'][0]['geometry']['location']['lng']

    return lat, lon


# @lru_cache
def get_gridpoints_by_lat_lon(lat, lon) -> str:
    r = requests.get(f'https://api.weather.gov/points/{lat},{lon}')

    write_local_file("points", r.json())
    
    gridId = r.json()['properties']['gridId']
    gridX = r.json()['properties']['gridX']
    gridY = r.json()['properties']['gridY']

    return gridId, gridX, gridY


# @lru_cache
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

# def set_alert():

# def 

if __name__ == '__main__':
    
    load_dotenv()
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB')

    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    lat, lon = get_lat_lon_for_address('8203 Metcalf Drive Richmond VA 23227')
    gridId, gridX, gridY = get_gridpoints_by_lat_lon(lat, lon)
    whole_forecast = get_whole_forecast(gridId, gridX, gridY)
    event_time = '2023-12-01T11:30:00-05:00'
    period_forecast = get_forecast_for_period(whole_forecast, event_time)
    print(period_forecast)

