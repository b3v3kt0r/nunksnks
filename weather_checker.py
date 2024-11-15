import os

import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("WEATHER_API_KEY")
BASE_URL = os.environ.get("WEATHER_BASE_URL")


def get_weather(city) -> dict | None:
    try:
        res = requests.get(BASE_URL, params={"key": API_KEY, "q": city})
        res.raise_for_status()
        data = res.json()

        location_name = data["location"]["name"]
        location_country = data["location"]["country"]
        localtime = data["location"]["localtime"]
        temp_c = data["current"]["temp_c"]
        condition_text = data["current"]["condition"]["text"]

        return f"{location_name}/{location_country}\n{localtime}\nWeather: {temp_c} Celsius, {condition_text}"


    except requests.RequestException as e:
        print(f"Network or HTTP error occurred: {e}")
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
    except KeyError as e:
        print(f"Missing expected key in the response: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
