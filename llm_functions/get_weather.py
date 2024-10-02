import openmeteo_requests


import requests_cache
import pandas as pd
from retry_requests import retry

definition = {
    "name": "get_weather",
    "description": "Get the current weather for a given location",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "The latitude of the location"
            },
            "longitude": {
                "type": "number",
                "description": "The longitude of the location"
            }
        },
        "required": ["latitude", "longitude"]
    }
}

def get_weather(latitude, longitude):
    # This function should return the weather for the given location
    
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)


    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "apparent_temperature", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover"],
        "hourly": "temperature_2m",
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_apparent_temperature = current.Variables(1).Value()
    current_precipitation = current.Variables(2).Value()
    current_rain = current.Variables(3).Value()
    current_showers = current.Variables(4).Value()
    current_snowfall = current.Variables(5).Value()
    current_weather_code = current.Variables(6).Value()
    current_cloud_cover = current.Variables(7).Value()

    current_weather = {
        "temperature_2m": current_temperature_2m,
        "apparent_temperature": current_apparent_temperature,
        "precipitation": current_precipitation,
        "rain": current_rain,
        "showers": current_showers,
        "snowfall": current_snowfall,
        "weather_code": current_weather_code,
        "cloud_cover": current_cloud_cover

    }
    return current_weather