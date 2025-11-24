# Import the libraries
import streamlit as st
import streamlit.components.v1 as components  # noqa: F401
import pandas as pd  # noqa: F401
from datetime import datetime  # noqa: F401
from datetime import date
import altair as alt  # noqa: F401



# Import the data 
from data.api.apod_api import get_apod
from data.api.weather_api import get_weather
from data.api.neo_api import get_neo
from data.dataframes.weather_df import weather_to_df
from data.dataframes.neo_df import neo_to_dataframe
from data.dataframes.locations import LOCATIONS_SWEDEN


# Load the data
data = get_apod()


# Import the graphs
from graphs.weather_charts import cloud_visibility_chart, temp_humidity_chart  # noqa: E402
from graphs.neo_charts import neo_summary_metrics, neo_scatter_plot  # noqa: E402
from graphs.stargazing_score import compute_stargazing_score, plot_stargazing_score  # noqa: E402



# helper function for the fucking APOD banner
def apod_banner(url: str, height: int = 350):
    st.markdown(
        f"""
        <div style="
            width: 100%;
            max-height: {height}px;
            overflow: hidden;
            border-radius: 10px;
        ">
            <img src="{url}"
                 style="width: 100%; height: 100%; object-fit: cover;">
        </div>
        """,
        unsafe_allow_html=True
    )
## Set up the layout of the dashboard
st.set_page_config(page_title="Astral Forecast", layout="wide")

# get the apod image and data
data = get_apod()

st.title("Astral Forecast")

# Short intro
st.write("Clear skies or cosmic chaos? Sweden’s stargazing conditions tonight.")

# Banner using the helper function
apod_banner(data["url"], height=350)

# Explanation text
with st.expander("About today's image"):
    st.write(data["explanation"])

st.markdown("---")

# Short description of what my dash/app does
st.write("Discover where in Sweden the skies are clear tonight—track cloud cover, visibility, moonlight, and nearby asteroids.")

# LOCATION SELECTION 
st.header("Choose your stargazing location")

location_name = st.selectbox("Location", list(LOCATIONS_SWEDEN.keys()))
coords = LOCATIONS_SWEDEN[location_name]

tab1, tab2, tab3, tab4= st.tabs(["Overview", "Weather Overview", "Near-Earth Objects", "Stargazing Score"])

with tab1:

    if coords is not None:
        lat, lon = coords

        # Fetch data *for this location*
        raw_weather = get_weather(lat, lon)
        df_hours, astro_info = weather_to_df(raw_weather)

        # Fetch today's NEO data
        today = date.today()
        raw_neo = get_neo(today)
        neo_df = neo_to_dataframe(raw_neo)

        # Only looking at nighttime hours for now
        night = df_hours[df_hours["is_day"] == 0].copy()

        st.subheader(f"Tonight in {location_name}")

        col_a, col_b, col_c, col_d = st.columns(4, border=True)

        with col_a:
            st.metric(
                "🌙 Moon phase",
                astro_info["moon_phase"],
                f"{astro_info['moon_illumination']}% illuminated"
            )
        with col_b:
            min_cloud = int(night["cloud_cover"].min())
            st.metric("☁️ Cloud coverage (night)", f"{min_cloud}%")

        with col_c:
            max_vis = night["visibility_km"].max()
            st.metric("🔭 Max visibility (night)", f"{max_vis:.1f} km")

        with col_d:
            st.metric(
                "☀️ Sunset",
                astro_info["sunset"]
            )
    else:
        st.info("Custom coordinates not implemented yet.")

with tab2:
    st.subheader("Cloud cover & visibility (night hours)")
    cloud_visibility_chart(night)
    st.caption(
        "**Solid line** = Cloud cover (%) — lower is better\n"
        "**Dashed gray line** = Visibility (km) — higher is better"
    )

    st.subheader("Temperature & humidity (night hours)")
    temp_humidity_chart(night)
    st.caption(
        "**Solid line** = Temperature (°C)\n"
        "**Dashed gray line** = Humidity (%) — higher humidity means haze & condensation"
    )

with tab3:
    st.subheader("Today's near-Earth objects")

    neo_summary_metrics(neo_df)

    st.markdown("#### Size vs distance")
    neo_scatter_plot(neo_df)
    st.caption(
        "Points further left are closer to Earth (in Moon–Earth distances); "
        "points higher up are larger asteroids. Red markers are classified as potentially hazardous."
    )

with tab4:
    st.subheader(f"✨ Stargazing score for tonight in {location_name}")

    score_df = compute_stargazing_score(night, astro_info)

    overall_score = score_df["score"].mean()

    col1, col2 = st.columns(2, gap="large", border=True)

    with col1:
        st.metric("Overall stargazing score (night)", f"{overall_score:.0f} / 100")

    # score verdict
    score_10 = overall_score / 10
    if score_10 >= 8:
        verdict = "✨ Incredible night — go outside!"
    elif score_10 >= 6:
        verdict = "🌙 Pretty good — worth a look."
    elif score_10 >= 4:
        verdict = "🌥 Meh — sky conditions mixed."
    else:
        verdict = "☁ Not a great night for stargazing."
    with col2:
        st.markdown(f"### {verdict}")

    # Chart
    st.markdown("#### Score by hour (night only)")
    plot_stargazing_score(score_df, location_name)









