import requests
from typing import Dict

from chatlas import ChatAnthropic
from dotenv import load_dotenv
from shiny.express import ui

load_dotenv(verbose=False)


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


chat_client = ChatAnthropic()

chat_client.register_tool(get_coordinates)
chat_client.register_tool(get_weather)

chat = ui.Chat(id="chat")
chat.ui(
    messages=[
        "Hello! I am a weather bot! Where would you like to get the weather form?"
    ]
)


@chat.on_user_submit
async def _(user_input: str):
    response = await chat_client.stream_async(user_input, content="all")
    await chat.append_message_stream(response)
