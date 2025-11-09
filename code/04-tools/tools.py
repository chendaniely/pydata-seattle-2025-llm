import requests
from typing import Dict

from chatlas import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()


def get_coordinates(location: str) -> Dict[str, float]:
    base_url: str = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location,
        "format": "json",
        "limit": 1,  # only return the top result
        "addressdetails": 1,  # include detailed address info
    }

    headers = {"User-Agent": "example_weather/1.0 (daniel.chen@posit.co)"}
    response = requests.get(
        base_url,
        params=params,
        headers=headers,
    )

    data = response.json()

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])

    return {"lat": lat, "lon": lon}


def get_weather(lat: float, lon: float):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
    }

    response = requests.get(
        base_url,
        params=params,
    )

    data = response.json()

    return {k: v for k, v in data.items()}


chat = ChatAnthropic(
    system_prompt=(
        "You are a helpful assistant that can check the weather. "
        "Report results in imperial units."
    ),
)

# chat.list_models()

chat.register_tool(get_weather)
chat.register_tool(get_coordinates)
chat.chat("What is the weather in Seattle?")
