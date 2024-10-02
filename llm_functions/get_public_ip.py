
import json
from urllib3 import request

definition = {
    "name": "get_public_ip",
    "description": "Get the local IP address of the machine.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}



def get_public_ip():
    """
    Get the public IP address of the machine.
    """
    url = 'http://ipinfo.io/json'
    response = request("GET",url).data.decode('utf-8')
    data = json.loads(response)

    ip=data['ip']
    return ip