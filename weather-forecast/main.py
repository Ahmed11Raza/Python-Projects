# weather_app.py
import uvicorn
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from fastapi import FastAPI
from datetime import datetime, timedelta
import json

# Initialize FastAPI app
api = FastAPI(title="Weather Forecast API")

# OpenWeatherMap API key - replace with your own API key
API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

@api.get("/weather/{city}")
async def get_weather(city: str):
    """Fetch 5-day weather forecast for a given city"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"  # Use Celsius
    }
    
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch weather data: {response.status_code}"}

# Streamlit UI
st.set_page_config(
    page_title="Weather Forecast App",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Weather Forecast Application")
st.write("Enter a city name to get a 5-day weather forecast")

# User input
city = st.text_input("City name", "London")
if st.button("Get Forecast"):
    # Show loading spinner
    with st.spinner("Fetching weather data..."):
        # Request to our FastAPI backend
        response = requests.get(f"http://localhost:8000/weather/{city}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "error" in data:
                st.error(data["error"])
            else:
                # Extract city information
                city_info = data["city"]
                st.subheader(f"Weather forecast for {city_info['name']}, {city_info['country']}")
                
                # Process forecast data
                forecasts = data["list"]
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["Summary", "Detailed Forecast", "Temperature Chart"])
                
                with tab1:
                    # Show current weather
                    current = forecasts[0]
                    current_temp = current["main"]["temp"]
                    current_weather = current["weather"][0]["description"]
                    current_icon = current["weather"][0]["icon"]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### Current Weather")
                        st.markdown(f"**Temperature:** {current_temp}°C")
                        st.markdown(f"**Conditions:** {current_weather.title()}")
                        st.markdown(f"**Humidity:** {current['main']['humidity']}%")
                        st.markdown(f"**Wind:** {current['wind']['speed']} m/s")
                    
                    with col2:
                        # Display weather icon
                        icon_url = f"http://openweathermap.org/img/wn/{current_icon}@2x.png"
                        st.image(icon_url, width=100)
                    
                    # Display today's forecast summary
                    st.markdown("### Today's Forecast")
                    today_forecasts = [f for f in forecasts if datetime.fromtimestamp(f["dt"]).date() == datetime.today().date()]
                    
                    # Create columns for each time period
                    cols = st.columns(len(today_forecasts))
                    for i, forecast in enumerate(today_forecasts):
                        time = datetime.fromtimestamp(forecast["dt"]).strftime("%H:%M")
                        temp = forecast["main"]["temp"]
                        weather = forecast["weather"][0]["description"]
                        icon = forecast["weather"][0]["icon"]
                        
                        cols[i].markdown(f"**{time}**")
                        cols[i].image(f"http://openweathermap.org/img/wn/{icon}.png", width=50)
                        cols[i].markdown(f"{temp}°C")
                        cols[i].markdown(f"{weather.title()}")
                
                with tab2:
                    # Group forecasts by date
                    forecast_by_day = {}
                    for forecast in forecasts:
                        date = datetime.fromtimestamp(forecast["dt"]).date()
                        if date not in forecast_by_day:
                            forecast_by_day[date] = []
                        forecast_by_day[date].append(forecast)
                    
                    # Display forecasts by day
                    for date, day_forecasts in forecast_by_day.items():
                        st.markdown(f"### {date.strftime('%A, %B %d')}")
                        
                        # Create a dataframe for the day's forecasts
                        df_data = []
                        for f in day_forecasts:
                            time = datetime.fromtimestamp(f["dt"]).strftime("%H:%M")
                            df_data.append({
                                "Time": time,
                                "Temperature (°C)": f["main"]["temp"],
                                "Feels Like (°C)": f["main"]["feels_like"],
                                "Weather": f["weather"][0]["description"].title(),
                                "Humidity (%)": f["main"]["humidity"],
                                "Wind (m/s)": f["wind"]["speed"],
                                "Pressure (hPa)": f["main"]["pressure"]
                            })
                        
                        df = pd.DataFrame(df_data)
                        st.dataframe(df, use_container_width=True)
                
                with tab3:
                    # Prepare data for temperature chart
                    times = [datetime.fromtimestamp(f["dt"]) for f in forecasts]
                    temps = [f["main"]["temp"] for f in forecasts]
                    feels_like = [f["main"]["feels_like"] for f in forecasts]
                    
                    # Create temperature chart
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(times, temps, 'b-', label='Temperature')
                    ax.plot(times, feels_like, 'r--', label='Feels Like')
                    ax.set_xlabel('Date & Time')
                    ax.set_ylabel('Temperature (°C)')
                    ax.set_title('Temperature Forecast')
                    ax.grid(True)
                    ax.legend()
                    
                    # Format x-axis to show dates better
                    fig.autofmt_xdate()
                    
                    st.pyplot(fig)
        else:
            st.error(f"Error: Could not fetch weather data (Status code: {response.status_code})")

# Run both Streamlit and FastAPI apps
def run_api():
    """Run the FastAPI application with uvicorn"""
    uvicorn.run(api, host="0.0.0.0", port=8000)



    
