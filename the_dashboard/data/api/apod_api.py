import requests
import streamlit as st
from datetime import date

API_KEY = st.secrets["APOD_KEY"]

def get_apod(apod_date: date | None = None) -> dict:

    url = "https://api.nasa.gov/planetary/apod"
    
    params = {
        "api_key": API_KEY,
    }
    if apod_date is not None:
        params["date"] = apod_date.strftime("%Y-%m-%d")
        
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
