from urllib3 import request
import json


definition = {
    "name": "get_aprox_location",
    "description": "Get the location information",
    "parameters": {
        "type": "object",
        "properties": {
        },
        "required": []
    }
}

def get_aprox_location():
    """
    Get the location information from an IP address.
    """
    url = 'http://ipinfo.io/json'
    response = request("GET",url).data.decode('utf-8')
    data = json.loads(response)

    IP=data['ip']
    org=data['org']
    city = data['city']
    country=data['country']
    region=data['region']
    return {
        "city": city,
        "country": country,
        "region": region
    }
