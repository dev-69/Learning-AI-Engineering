from datetime import datetime
import requests
import json
from utilities.utilities import log 
from google import genai
from google.genai.errors import APIError

gemini_client = genai.Client()

def run_tool(tool_call):
    func_name = tool_call.function.name
    func_args = {}

    try: 
        func_args = json.loads(tool_call.function.arguments or "{}")
        log(f"  [TOOL] Calling {func_name}({func_args})")
        fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
        result = fn(**func_args)
    except Exception as e: 
        result = f"Error while running the function {func_name} : {e}"

    log(f"  [TOOL_RESULT]{result}")    
    return str(result)

def ask_gemini(question: str) -> str:
    try:
        # Use a Flash model (best free-tier rate limits)
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=question,
        )
        return response.text or "Gemini returned an empty response"
    except APIError as e:
        if e.code == 429:
            return "Gemini free tier rate limit reached. Try again in a minute."
        return f"Gemini API error: {e.message}"

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
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
        "type": "function",
        "function": {
            "name": "ask_gemini",
            "description": "Ask Gemini a question. ALWAYS call this tool when the user says 'ask gemini' or when local knowledge is not enough.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The exact question to send to Gemini"
                    }
                },
                "required": ["question"]
            },
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
    "ask_gemini" : ask_gemini,
    "get_current_time" : get_current_time,
    "get_city_weather" : get_city_weather,
    "get_user_city" : get_user_city
}

