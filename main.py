import requests
import json
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

"""
Docs for Weather API https://www.weather.gov/documentation/services-web-api#/
"""

def get_lat_lon_for_address(address_string):
    
    address_encoded = urllib.parse.quote_plus(address_string)

    # https://developers.google.com/maps/documentation/geocoding/requests-geocoding#geocoding-lookup
    r = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address_encoded}&key={GOOGLE_API_KEY}')

    # Serializing json
    response = json.dumps(r.json(), indent=4)
 
    # Writing to sample.json
    with open("geocodes.json", "w") as outfile:
        outfile.write(response)
    
    # gridId = r.json()['properties']['gridId']
    # gridX = r.json()['properties']['gridX']
    # gridY = r.json()['properties']['gridY']

    # hardcoded values
    lat = 37.632040
    lon = -77.444820

    return lat, lon


def get_gridpoints_by_lat_lon(lat, lon) -> str:
    r = requests.get(f'https://api.weather.gov/points/{lat},{lon}')

    # Serializing json
    response = json.dumps(r.json(), indent=4)
 
    # Writing to sample.json
    with open("points.json", "w") as outfile:
        outfile.write(response)
    
    gridId = r.json()['properties']['gridId']
    gridX = r.json()['properties']['gridX']
    gridY = r.json()['properties']['gridY']

    return gridId, gridX, gridY


def get_whole_forecast(gridId, gridX, gridY) -> dict:
    r = requests.get(f'https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast')

    # Serializing json
    json_object = json.dumps(r.json(), indent=4)
 
    # Writing to sample.json
    with open("forecast.json", "w") as outfile:
        outfile.write(json_object)

    forecast = r.json()['properties']['periods']

    return forecast

import datetime 

def get_forecast_for_period(whole_forecast: dict, event_time) -> dict:


    for period_forecast in whole_forecast:
        if event_time >= period_forecast['startTime'] and event_time <= period_forecast['endTime']:
            # Writing to sample.json
            with open("period_forecast.json", "w") as outfile:
                outfile.write(period_forecast)
        else:
            message = '{"no forecast found"}'
            # Writing to sample.json
            with open("period_forecast.json", "w") as outfile:
                outfile.write(message)


# def set_alert():

# def 

lat, lon = get_lat_lon_for_address('8203 Metcalf Drive, Richmond, VA 23227')
# gridId, gridX, gridY = get_gridpoints_by_lat_lon(lat, lon)
# whole_forecast = get_whole_forecast(gridId, gridX, gridY)
# event_time = '023-11-21T11:30:00-05:00'
# get_forecast_for_period(whole_forecast, event_time)

