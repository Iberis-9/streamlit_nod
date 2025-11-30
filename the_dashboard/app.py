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



# Import the graphs
from graphs.weather_charts import cloud_visibility_chart, temp_humidity_chart  # noqa: E402
from graphs.neo_charts import neo_summary_metrics, neo_scatter_plot  # noqa: E402
from graphs.stargazing_score import compute_stargazing_score, plot_stargazing_score  # noqa: E402

# Fetching/Loading and caching data from APIs

# Wrapping the apis in @st.cache_data to cache results and avoid hitting rate limits/reduce lag
@st.cache_data(ttl = 72000) # setting it to 20 hours as APOD only updates once a day
def get_apod_cached():
    return get_apod()

@st.cache_data(ttl = 1800)
def get_weather_cached(lat, lon):
    raw_weather = get_weather(lat, lon)
    df_hours, astro_info = weather_to_df(raw_weather)
    return df_hours, astro_info

@st.cache_data(ttl = 3600)
def get_neo_cached(date):
    raw_neo = get_neo(date)
    neo_df = neo_to_dataframe(raw_neo)
    return neo_df


# helper function for the APOD banner
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
data = get_apod_cached()

st.title("Astral Forecast")

# Short intro
st.write("Clear skies or cosmic chaos? Sweden’s stargazing conditions tonight.")

# Banner using the helper function
apod_banner(data["url"], height=350)


# Explanation text and link to full-res image
with st.expander("About today's image"):
    st.write(data["explanation"])
    if "hdurl" in data:
        st.markdown(f"[🔗 View full-resolution image]({data['hdurl']})")
    else:
        st.markdown(f"[🔗 View full image]({data['url']})")

st.markdown("---")

# Short description of what my dash/app does
st.write("Discover where in Sweden the skies are clear tonight—track cloud cover, visibility, moonlight, and nearby asteroids.")

# LOCATION SELECTION 
st.header("Choose your stargazing location")

location_name = st.selectbox("Location", list(LOCATIONS_SWEDEN.keys()))
coords = LOCATIONS_SWEDEN[location_name]


night = None
astro_info = None
neo_df = None

if coords is not None:
    lat, lon = coords

    # Fetch weather data for this location (cached)
    df_hours, astro_info = get_weather_cached(lat, lon)

    # Fetch today's NEO data (cached)
    today = date.today()
    neo_df = get_neo_cached(today)

    # Only looking at nighttime hours for now
    night = df_hours[df_hours["is_day"] == 0].copy()
else:
    st.info("Custom coordinates not implemented yet.")


# Different sections/tabs for different parts of the dashboard
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Weather Overview", "Near-Earth Objects", "Stargazing Score"]
)

#  Tab 1: Overview 

with tab1:
    if night is None or astro_info is None:
        st.warning("Select a location to see tonight's overview.")
    else:
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
            st.metric("☀️ Sunset", astro_info["sunset"])

# Tab 2: Weather Overview 

with tab2:
    if night is None:
        st.warning("Select a location to see weather details.")
    else:
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
            "**Dashed gray line** = Humidity (%) — "
            "higher humidity means haze & condensation"
        )

# Tab 3: Near-Earth Objects 

with tab3:
    if neo_df is None:
        st.warning("Select a location to see NEO data.")
    else:
        st.subheader("Today's near-Earth objects")

        neo_summary_metrics(neo_df)

        st.markdown("#### Size vs distance")
        neo_scatter_plot(neo_df)
        st.caption(
            "Points further left are closer to Earth (in Moon–Earth distances); "
            "points higher up are larger asteroids. Red markers are classified as potentially hazardous."
        )

# Tab 4: Stargazing Score 

with tab4:
    if night is None or astro_info is None:
        st.warning("Select a location to see the stargazing score.")
    else:
        st.subheader(f"✨ Stargazing score for tonight in {location_name}")

        score_df = compute_stargazing_score(night, astro_info)
        overall_score = score_df["score"].mean()

        col1, col2 = st.columns(2, gap="large", border=True)

        with col1:
            st.metric("Overall stargazing score (night)", f"{overall_score:.0f} / 100")

        # Score verdict
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









