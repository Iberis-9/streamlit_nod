import requests
import streamlit as st
from datetime import date

API_KEY = st.secrets["NEO_KEY"]

def get_neo(target_date: date) -> dict:

    url = "https://api.nasa.gov/neo/rest/v1/feed"
    date_str = target_date.strftime("%Y-%m-%d")
    
    params = {
        "api_key": API_KEY,
        "start_date": date_str,
        "end_date": date_str,  
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
