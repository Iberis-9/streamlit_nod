import pandas as pd
from typing import Dict, Any, Tuple

def weather_to_df(raw: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:

    forecastday = raw["forecast"]["forecastday"][0]

    # Hourly data 
    hours = forecastday["hour"]
    df_hours = pd.json_normalize(hours)

    # Keep only the columns I need
    keep_cols = [
        "time",
        "temp_c",
        "cloud",
        "humidity",
        "is_day",
        "condition.text",
        "condition.icon",
        "vis_km"
    ]
    df_hours = df_hours[keep_cols]

    # Rename for convenience
    df_hours = df_hours.rename(columns={
        "time": "datetime",
        "temp_c": "temp_c",
        "cloud": "cloud_cover",
        "condition.text": "condition",
        "vis_km": "visibility_km",
    })

    # Convert datetime to actual datetime type
    df_hours["datetime"] = pd.to_datetime(df_hours["datetime"])

    # Astro block
    astro = forecastday["astro"]
   
    # getting data on sunrise, sunset, moonrise, moonset, moon_phase, moon_illumination
    astro_info = {
        "sunrise": astro.get("sunrise"),
        "sunset": astro.get("sunset"),
        "moonrise": astro.get("moonrise"),
        "moonset": astro.get("moonset"),
        "moon_phase": astro.get("moon_phase"),
        "moon_illumination": astro.get("moon_illumination"),
    }

    return df_hours, astro_info
