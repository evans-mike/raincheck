import requests
import json

"""
Docs for Weather API https://www.weather.gov/documentation/services-web-api#/
"""

def get_lat_lon_for_location():
    lat = 37.632040
    lon = -77.444820
    return lat, lon

def get_gridpoints_by_lat_lon(lat, lon):
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

def get_forecast_for_timeperiod(response: dict, timeperiod) -> dict:
    return timeperiod

# def set_alert():

# def 

lat, lon = get_lat_lon_for_location()
gridId, gridX, gridY = get_gridpoints_by_lat_lon(lat, lon)
get_whole_forecast(gridId, gridX, gridY)