from datetime import datetime
import os
from dotenv import load_dotenv

import httpx
import json

load_dotenv()

API_KEY = os.environ.get("WEATHER_API_KEY")
BASE_URL = os.environ.get("WEATHER_BASE_URL")


def get_weather(client: httpx.Client, city) -> dict | None:
    try:
        response = client.get(BASE_URL,
                    params={"key": API_KEY, "q": city})
        response.raise_for_status()
        data = response.json()

        temperature = {
            "city": city,
            "temperature": data["current"]["temp_c"],
            "date_time": datetime.now()
        }
        return temperature

    except httpx.RequestError as e:
        print(f"Network or HTTP error occurred: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None
    except KeyError as e:
        print(f"Missing expected key in the response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
