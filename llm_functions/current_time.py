import datetime

definition = {
    "name": "current_time",
    "description": "Get the current time.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}



def current_time():
    """
    Get the current time.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")   