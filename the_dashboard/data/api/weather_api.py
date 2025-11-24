import requests
import streamlit as st

API_KEY = st.secrets["WEATHER_KEY"] 

def get_weather(lat: float, lon: float):
    """
    Fetch 24 hours of forecast + sun/moon astro data
    for the given latitude/longitude.
    """
    url = "https://api.weatherapi.com/v1/forecast.json"
    
    params = {
        "key": API_KEY,
        "q": f"{lat},{lon}",
        "days": 1,        # 1 day should be enough for stargazing 
        "aqi": "no",
        "alerts": "no"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
