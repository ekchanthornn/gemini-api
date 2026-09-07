from dotenv import load_dotenv
from google import genai
import os
import requests

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def get_weather(city):
    cities = {
        "Phnom Penh": {
            "latitude": 11.5564,
            "longitude": 104.9282
        },
        "Siem Reap": {
            "latitude": 13.3633,
            "longitude": 103.8564
        },
        "Battambang": {
            "latitude": 13.0957,
            "longitude": 103.2022
        }
    }

    if city not in cities:
        return {
            "error": f"មិនស្គាល់ទីក្រុង {city}"
        }

    latitude = cities[city]["latitude"]
    longitude = cities[city]["longitude"]

    # Call Weather API
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
    }

    response = requests.get(url, params=params)

    # Check HTTP error
    response.raise_for_status()

    data = response.json()

    current = data["current"]

    return {
        "city": city,
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "precipitation": current["precipitation"],
        "wind_speed": current["wind_speed_10m"],
        "weather_code": current["weather_code"]
    }
    
# Define Tool (Function)
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "ទទួលព័ត៌មានអាកាសធាតុតាមទីក្រុង",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "ឈ្មោះទីក្រុង"
                }
            },
            "required": ["city"]
        }
    }
]

interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="អាកាសធាតុភ្នំពេញថ្ងៃនេះ?",
    tools=tools
)

for step in interaction.steps:
    if step.type == "function_call":
        print("Gemini ចង់ហៅ function:")
        print("Function:", step.name)
        print("Arguments:", step.arguments)
        city = step.arguments["city"]
        weather_result = get_weather(city)
        print("\nWeather API Result:")
        print(weather_result)
        interaction2 = client.interactions.create(
            model="gemini-3.5-flash-lite",

            input=[
                {
                    "type": "function_result",
                    "name": step.name,
                    "result": weather_result
                }
            ],
            previous_interaction_id=interaction.id
        )
        print("\nGemini Final Answer:")
        print(interaction2.output_text)

