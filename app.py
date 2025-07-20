import os
from dotenv import load_dotenv
import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="Airline Booking Dashboard", layout="wide")
st.title("Airline Booking Dashboard")

# User selection
airport = st.selectbox(
    "Select Your Airport", 
    options=["BOM", "DEL", "JAI", "LKO", "MAA", "CCU"],
    index=0
)


# API credentials
API_KEY = os.getenv("API_KEY")
API_URL = "http://api.aviationstack.com/v1/flights"

@st.cache_data(show_spinner="Fetching flight data...")
def fetch_flight_data(origin_airport):
    params = {
        "access_key": API_KEY,
        "dep_iata": origin_airport,
        "limit": 100
    }
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        flights = response.json().get("data", [])
        return pd.DataFrame(flights)
    except requests.RequestException as e:
        st.error(f"API request failed: {e}")
        return pd.DataFrame()

# Load data
df = fetch_flight_data(airport)

if df.empty:
    st.warning("No flight data found at this time. Please try a different airport or come back later.")
else:
    # Data preparation
    df_clean = pd.DataFrame({
        "Flight Number": df["flight"].apply(lambda x: x.get("iata") if x else None),
        "Airline": df["airline"].apply(lambda x: x.get("name") if x else None),
        "Destination": df["arrival"].apply(lambda x: x.get("iata") if x else None),
        "Departure Time": df["departure"].apply(lambda x: x.get("scheduled") if x else None),
    }).dropna()

    # Display
    st.subheader(f"Flights Departing from {airport}")
    st.dataframe(df_clean)

    # Top destinations analysis
    top_destinations = (
        df_clean["Destination"]
        .value_counts()
        .head(10)
        .reset_index()
        .rename(columns={"index": "Destination", "Destination": "Flight Count"})
    )

    # Matplotlib visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_destinations["Destination"], top_destinations["Flight Count"], color="#3399FF", edgecolor="black")
    ax.set_title(f"Top 10 Destinations from {airport}", fontsize=16, weight="bold")
    ax.set_xlabel("Destination Airport", fontsize=12)
    ax.set_ylabel("Number of Departing Flights", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)

