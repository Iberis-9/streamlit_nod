import pandas as pd
from datetime import date
from typing import Dict, Any

def neo_to_dataframe(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """Convert NASA NEO API daily feed into a clean pandas DataFrame."""
    
    # Identify the date key (NASA groups objects by date)
    date_key = list(raw_data["near_earth_objects"].keys())[0]
    
    # Flatten close-approach data & pull asteroid-level metadata into columns
    df = pd.json_normalize(
        raw_data["near_earth_objects"][date_key],
        record_path=["close_approach_data"],
        meta=[
            "name",
            "absolute_magnitude_h",
            "is_potentially_hazardous_asteroid",
            ["estimated_diameter", "kilometers", "estimated_diameter_min"],
            ["estimated_diameter", "kilometers", "estimated_diameter_max"],
        ],
        errors="ignore"
    )
    
    # Rename columns to something readable
    df = df.rename(columns={
        "relative_velocity.kilometers_per_second": "velocity_km_s",
        "miss_distance.kilometers": "miss_distance_km",
        "miss_distance.lunar": "miss_distance_lunar",
        "estimated_diameter.kilometers.estimated_diameter_min": "diameter_km_min",
        "estimated_diameter.kilometers.estimated_diameter_max": "diameter_km_max",
        "is_potentially_hazardous_asteroid": "hazardous"
    })
    
    # Clean formatting
    # Convert to numeric if needed
    numeric_cols = ["velocity_km_s", "miss_distance_km", "miss_distance_lunar", "diameter_km_min", "diameter_km_max"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute average diameter column
    if "diameter_km_min" in df.columns and "diameter_km_max" in df.columns:
        df["diameter_km_avg"] = (df["diameter_km_min"] + df["diameter_km_max"]) / 2
    
    return df
