import requests
from PIL import Image, ImageTk
import tkinter as tk
from io import BytesIO

API_KEY = "OPENWHETHER_API_KEY" # Replace with your OpenWeatherMap API key
BASE_URL = "https://api.openweathermap.org/data/2.5/"

def get_current_weather(city, units="metric"):
    """
    Fetch current weather data for a given city.
    Units: 'metric' for Celsius, 'imperial' for Fahrenheit.
    """
    url = f"{BASE_URL}weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"]
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching current weather: {e}")

def get_forecast(city, units="metric"):
    """
    Fetch 5-day hourly forecast for a given city.
    Returns list of hourly data and daily summaries.
    """
    url = f"{BASE_URL}forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        hourly = []
        daily = {}
        for item in data["list"][:40]:  # First 5 days, 3-hour intervals
            dt = item["dt_txt"]
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]
            icon = item["weather"][0]["icon"]
            wind = item["wind"]["speed"]
            hourly.append({
                "time": dt,
                "temperature": temp,
                "description": desc,
                "icon": icon,
                "wind_speed": wind
            })
        
        # Simple daily summary (group by day)
        for item in data["list"]:
            day = item["dt_txt"][:10]  # YYYY-MM-DD
            if day not in daily:
                daily[day] = {
                    "min_temp": item["main"]["temp_min"],
                    "max_temp": item["main"]["temp_max"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"]
                }
            else:
                daily[day]["min_temp"] = min(daily[day]["min_temp"], item["main"]["temp_min"])
                daily[day]["max_temp"] = max(daily[day]["max_temp"], item["main"]["temp_max"])
        
        return {"hourly": hourly, "daily": list(daily.values())}
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching forecast: {e}")

def get_weather_icon(icon_code, size=(64, 64)):
    """
    Download and return weather icon as PhotoImage for Tkinter.
    """
    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    try:
        response = requests.get(icon_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching icon: {e}")
