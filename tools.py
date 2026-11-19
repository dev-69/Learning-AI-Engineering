from datetime import datetime
import requests

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10)
    return response.text

def get_user_city():
    return "Mumbai"

TOOLS = [
    {
        "type" :"function",
        "function" : {
            "name" : "get_current_time",
            "description" : "returns the current date and time as a formatted string",
            "parameters" : { "type" : "object", "properties" : {}},
        }
    },
    {
        "type" :"function",
        "function" : {
            "name" : "get_user_city",
            "description" : "returns the user's current city. Use this when the user says 'my city', 'my location' without naming the city",
            "parameters" : { "type" : "object", "properties" : {}},
        }
    },

    {
        "type" :"function",
        "function" : {
            "name" : "get_city_weather",
            "description" : "returns the weather of a given city as a formatted string",
            "parameters" : { 
                "type" : "object", 
                "properties" : {
                    "city" : {
                        "type" : "string",
                        "description" : "name of the city"
                    }
                },
                "required" : ["city"]
            },
        },
    }
]

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time" : get_current_time,
    "get_city_weather" : get_city_weather,
    "get_user_city" : get_user_city
}