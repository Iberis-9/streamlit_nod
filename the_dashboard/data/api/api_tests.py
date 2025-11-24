

import json
from datetime import date
import requests
from data.api.neo_api import API_KEY

def get_neos_for_date(target_date: date):
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    date_str = target_date.strftime("%Y-%m-%d")
    params = {
        "api_key": API_KEY,
        "start_date": date_str,
        "end_date": date_str,
    }
    response = requests.get(url, params=params)
    return response.json()

data = get_neos_for_date(date.today())
print(json.dumps(data, indent=2))
