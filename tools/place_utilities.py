import urllib.parse
from functools import lru_cache
import requests
from dotenv import dotenv_values


config = dotenv_values(".env")


@lru_cache
def _get_lat_lon_for_address_google(address_str: str) -> tuple[float, float]:

    address_encoded = urllib.parse.quote_plus(address_str)

    r = requests.get(
        f'https://maps.googleapis.com/maps/api/geocode/json?key={config["GOOGLE_API_KEY"]}&address={address_encoded}'
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
