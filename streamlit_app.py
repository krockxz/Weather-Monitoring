import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Base URL of the FastAPI server
BASE_URL = "http://127.0.0.1:8000"

st.title("Weather Data Processing System")

# Section to fetch weather data for a city
st.header("Fetch Weather Data")
city = st.text_input("Enter city name", "Delhi")
if st.button("Fetch Weather"):
    response = requests.get(f"{BASE_URL}/fetch-weather/{city}")
    if response.status_code == 200:
        weather_data = response.json()
        st.write(weather_data)
    else:
        st.error("Error fetching weather data")

# Section to display daily weather summary
st.header("Daily Weather Summary")
if st.button("Get Daily Summary"):
    response = requests.get(f"{BASE_URL}/weather-summary/")
    if response.status_code == 200:
        summary = response.json()["daily_summary"]
        if summary:
            df_summary = pd.DataFrame(summary)
            df_summary['date'] = pd.to_datetime(df_summary['date'])

            st.write(df_summary)

            # Visualization for daily summaries
            fig_avg_temp = px.line(df_summary, x="date", y="avg_temp", color="city", title="Average Temperature per City",
                                   line_shape='linear', markers=True)
            fig_avg_temp.update_xaxes(dtick="D1", tickformat="%Y-%m-%d %H:%M")
            st.plotly_chart(fig_avg_temp)

            fig_max_temp = px.line(df_summary, x="date", y="max_temp", color="city", title="Maximum Temperature per City",
                                   line_shape='linear', markers=True)
            fig_max_temp.update_xaxes(dtick="D1", tickformat="%Y-%m-%d %H:%M")
            st.plotly_chart(fig_max_temp)

            fig_min_temp = px.line(df_summary, x="date", y="min_temp", color="city", title="Minimum Temperature per City",
                                   line_shape='linear', markers=True)
            fig_min_temp.update_xaxes(dtick="D1", tickformat="%Y-%m-%d %H:%M")
            st.plotly_chart(fig_min_temp)
            
            fig_condition = px.histogram(df_summary, x="dominant_condition", color="city", title="Dominant Weather Condition per City")
            st.plotly_chart(fig_condition)
        else:
            st.warning("No weather data found for summary")
    else:
        st.error("Error retrieving daily summary")

# Section to set alert thresholds
st.header("Set Alert Threshold")
threshold_city = st.text_input("City for threshold", "Delhi")
threshold_condition = st.text_input("Condition for threshold", "Clear")
threshold_temp = st.number_input("Temperature threshold (°C)", min_value=-50.0, max_value=50.0, value=35.0)
if st.button("Set Threshold"):
    response = requests.post(f"{BASE_URL}/set-threshold/", params={
        "city": threshold_city,
        "condition": threshold_condition,
        "temp_threshold": threshold_temp
    })
    if response.status_code == 200:
        st.success("Threshold set and checked!")
    else:
        st.error("Error setting threshold")

# Automatically fetch and display alerts
st.header("Alerts")
response = requests.get(f"{BASE_URL}/alerts/")
if response.status_code == 200:
    alerts = response.json()["alerts"]
    if alerts:
        df_alerts = pd.DataFrame(alerts)
        df_alerts['alert_time'] = pd.to_datetime(df_alerts['alert_time'], unit='s')  # Convert from Unix timestamp

        st.write(df_alerts)

        # Visualization for alerts
        fig_alerts = px.scatter(df_alerts, x="alert_time", y="temp_threshold", color="city", title="Temperature Alerts")
        st.plotly_chart(fig_alerts)
    else:
        st.warning("No alerts found")
else:
    st.error("Error retrieving alerts")
