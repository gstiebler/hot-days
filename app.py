import streamlit as st
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import plotly.express as px
import numpy as np
from datetime import datetime, date

# Configure Streamlit page
st.set_page_config(
    page_title="Temperature Analysis",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ Temperature Distribution Analysis")
st.markdown("Analyze the distribution of cold days based on minimum temperatures")
st.info("📊 **Data Source:** This application uses weather data from [Open-Meteo](https://open-meteo.com/), a free weather API providing historical weather data worldwide.")

# Setup the Open-Meteo API client with cache and retry on error
@st.cache_resource
def setup_api_client():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)  # Cache for 1 hour
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)

# Initialize session state for coordinates
if 'selected_latitude' not in st.session_state:
    st.session_state.selected_latitude = 52.52
if 'selected_longitude' not in st.session_state:
    st.session_state.selected_longitude = 13.41

# Create input form
with st.form("weather_form"):
    st.subheader("📍 Location and Date Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        latitude = st.number_input(
            "Latitude", 
            min_value=-90.0, 
            max_value=90.0, 
            value=st.session_state.selected_latitude,
            step=0.01,
            help="Enter latitude in decimal degrees (-90 to 90)"
        )
        
        start_date = st.date_input(
            "Start Date",
            value=date(2024, 1, 1),
            min_value=date(1940, 1, 1),
            max_value=date.today()
        )
    
    with col2:
        longitude = st.number_input(
            "Longitude", 
            min_value=-180.0, 
            max_value=180.0, 
            value=st.session_state.selected_longitude,
            step=0.01,
            help="Enter longitude in decimal degrees (-180 to 180)"
        )
        
        end_date = st.date_input(
            "End Date",
            value=date(2024, 12, 31),
            min_value=date(1940, 1, 1),
            max_value=date.today()
        )
    
    submit_button = st.form_submit_button("🔍 Analyze Temperature Data", type="primary")

# Process data when form is submitted
if submit_button:
    if start_date >= end_date:
        st.error("❌ Start date must be before end date!")
    else:
        try:
            with st.spinner("🌐 Fetching weather data..."):
                # Setup API client
                openmeteo = setup_api_client()
                
                # API parameters
                url = "https://archive-api.open-meteo.com/v1/archive"
                params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "daily": ["temperature_2m_max", "temperature_2m_min"]
                }
                
                # Fetch data
                responses = openmeteo.weather_api(url, params=params)
                response = responses[0]
                
                # Display location info
                st.success("✅ Data fetched successfully!")
                
                with st.expander("📊 Location Information"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Coordinates", f"{response.Latitude():.2f}°N, {response.Longitude():.2f}°E")
                    with col2:
                        st.metric("Elevation", f"{response.Elevation()} m")
                    with col3:
                        st.metric("Timezone", f"{response.Timezone()}")
                
                # Process daily data
                daily = response.Daily()
                daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
                daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
                
                # Create DataFrame
                daily_data = {
                    "date": pd.date_range(
                        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                        freq=pd.Timedelta(seconds=daily.Interval()),
                        inclusive="left"
                    ),
                    "temperature_2m_max": daily_temperature_2m_max,
                    "temperature_2m_min": daily_temperature_2m_min
                }
                
                df = pd.DataFrame(data=daily_data)
                
                # Remove any NaN values
                df = df.dropna()
                
                if len(df) == 0:
                    st.error("❌ No valid temperature data found for the selected period.")
                else:
                    # Create temperature distribution analysis
                    st.subheader("📈 Temperature Distribution Analysis")
                    
                    # Create temperature range for x-axis
                    min_temp = np.floor(df['temperature_2m_min'].min() * 5) / 5  # Round to nearest 0.2
                    max_temp = np.ceil(df['temperature_2m_min'].max() * 5) / 5   # Round to nearest 0.2
                    temp_range = np.arange(min_temp, max_temp + 0.2, 0.2)
                    
                    # Calculate number of days colder than each temperature
                    cold_days_count = []
                    for temp in temp_range:
                        cold_days = len(df[df['temperature_2m_min'] < temp])
                        cold_days_count.append(cold_days)
                    
                    # Create the chart
                    chart_data = pd.DataFrame({
                        'Temperature (°C)': temp_range,
                        'Days with Min Temp Below': cold_days_count
                    })
                    
                    # Create interactive plot with Plotly
                    fig = px.line(
                        chart_data, 
                        x='Temperature (°C)', 
                        y='Days with Min Temp Below',
                        title='Number of Days with Minimum Temperature Below Each Temperature Threshold',
                        labels={
                            'Temperature (°C)': 'Temperature Threshold (°C)',
                            'Days with Min Temp Below': 'Number of Days'
                        }
                    )
                    
                    fig.update_traces(line=dict(width=3, color='#FF6B6B'))
                    fig.update_layout(
                        xaxis_title="Temperature Threshold (°C)",
                        yaxis_title="Number of Days with Min Temp Below Threshold",
                        hovermode='x unified',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create maximum temperature distribution analysis
                    st.subheader("🔥 Maximum Temperature Distribution Analysis")
                    
                    # Create temperature range for x-axis (for maximum temperatures)
                    min_temp_max = np.floor(df['temperature_2m_max'].min() * 5) / 5  # Round to nearest 0.2
                    max_temp_max = np.ceil(df['temperature_2m_max'].max() * 5) / 5   # Round to nearest 0.2
                    temp_range_max = np.arange(min_temp_max, max_temp_max + 0.2, 0.2)
                    
                    # Calculate number of days hotter than each temperature
                    hot_days_count = []
                    for temp in temp_range_max:
                        hot_days = len(df[df['temperature_2m_max'] > temp])
                        hot_days_count.append(hot_days)
                    
                    # Create the chart for maximum temperatures
                    chart_data_max = pd.DataFrame({
                        'Temperature (°C)': temp_range_max,
                        'Days with Max Temp Above': hot_days_count
                    })
                    
                    # Create interactive plot with Plotly for maximum temperatures
                    fig_max = px.line(
                        chart_data_max, 
                        x='Temperature (°C)', 
                        y='Days with Max Temp Above',
                        title='Number of Days with Maximum Temperature Above Each Temperature Threshold',
                        labels={
                            'Temperature (°C)': 'Temperature Threshold (°C)',
                            'Days with Max Temp Above': 'Number of Days'
                        }
                    )
                    
                    fig_max.update_traces(line=dict(width=3, color='#FF8C42'))
                    fig_max.update_layout(
                        xaxis_title="Temperature Threshold (°C)",
                        yaxis_title="Number of Days with Max Temp Above Threshold",
                        hovermode='x unified',
                        height=500
                    )
                    
                    st.plotly_chart(fig_max, use_container_width=True)
                    
                    # Display summary statistics
                    st.subheader("📊 Temperature Summary")
                    
                    # Minimum temperature statistics
                    st.markdown("**Minimum Temperature Statistics**")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Total Days", 
                            len(df),
                            help="Total number of days with valid data"
                        )
                    
                    with col2:
                        st.metric(
                            "Coldest Day", 
                            f"{df['temperature_2m_min'].min():.1f}°C",
                            help="Lowest minimum temperature recorded"
                        )
                    
                    with col3:
                        st.metric(
                            "Warmest Min", 
                            f"{df['temperature_2m_min'].max():.1f}°C",
                            help="Highest minimum temperature recorded"
                        )
                    
                    with col4:
                        st.metric(
                            "Avg Min Temp", 
                            f"{df['temperature_2m_min'].mean():.1f}°C",
                            help="Average minimum temperature"
                        )
                    
                    # Maximum temperature statistics
                    st.markdown("**Maximum Temperature Statistics**")
                    col5, col6, col7, col8 = st.columns(4)
                    
                    with col5:
                        st.metric(
                            "Hottest Day", 
                            f"{df['temperature_2m_max'].max():.1f}°C",
                            help="Highest maximum temperature recorded"
                        )
                    
                    with col6:
                        st.metric(
                            "Coolest Max", 
                            f"{df['temperature_2m_max'].min():.1f}°C",
                            help="Lowest maximum temperature recorded"
                        )
                    
                    with col7:
                        st.metric(
                            "Avg Max Temp", 
                            f"{df['temperature_2m_max'].mean():.1f}°C",
                            help="Average maximum temperature"
                        )
                    
                    with col8:
                        st.metric(
                            "Temp Range", 
                            f"{df['temperature_2m_max'].max() - df['temperature_2m_min'].min():.1f}°C",
                            help="Difference between hottest max and coldest min"
                        )
                    
                    # Show raw data option
                    with st.expander("📋 View Raw Temperature Data"):
                        st.dataframe(
                            df.style.format({
                                'temperature_2m_max': '{:.1f}°C',
                                'temperature_2m_min': '{:.1f}°C'
                            }),
                            use_container_width=True
                        )
                        
                        # Download button for the data
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"temperature_data_{latitude}_{longitude}_{start_date}_{end_date}.csv",
                            mime="text/csv"
                        )
                
        except Exception as e:
            st.error(f"❌ Error fetching data: {str(e)}")
            st.info("💡 Please check your internet connection and try again. Make sure the date range is not too large.")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This application analyzes temperature data using the Open-Meteo API.
    
    **How to use:**
    1. Enter latitude and longitude coordinates
    2. Select your date range
    3. Click "Analyze Temperature Data"
    
    **Chart Explanation:**
    - The first chart shows how many days had a minimum temperature below each temperature threshold (cold days distribution)
    - The second chart shows how many days had a maximum temperature above each temperature threshold (hot days distribution)
    
    **Data Source:** [Open-Meteo API](https://open-meteo.com/)
    """)
    
    st.header("🌍 Popular Locations")
    locations = {
        "Rio de Janeiro, Brazil": (-22.91, -43.20),
        "Vancouver, Canada": (49.28, -123.12),
        "Paris, France": (48.85, 2.35),
        "Toronto, Canada": (43.65, -79.38),
        "São Paulo, Brazil": (-23.55, -46.63),
        "Calgary, Canada": (51.05, -114.07),
        "Berlin, Germany": (52.52, 13.41),
        "New York, USA": (40.71, -74.01),
        "Tokyo, Japan": (35.68, 139.69),
        "Sydney, Australia": (-33.87, 151.21),
        "London, UK": (51.51, -0.13),
    }
    
    for city, (lat, lon) in locations.items():
        if st.button(f"📍 {city}"):
            st.session_state.selected_latitude = lat
            st.session_state.selected_longitude = lon
            st.rerun()
