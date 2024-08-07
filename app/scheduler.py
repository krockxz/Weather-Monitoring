from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import requests
from .config import settings
from .crud import save_weather_data
import logging

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def fetch_weather_data(city: str):
    logger.info(f"Started fetching weather data for city: {city}")
    try:
        api_key = settings.openweather_api_key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_data = {
            'city': city,
            'main': data['weather'][0]['main'],
            'temp': data['main']['temp'] - 273.15,
            'feels_like': data['main']['feels_like'] - 273.15,
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'dt': data['dt']
        }
        logger.info(f"Weather data fetched for {city}: {weather_data}")
        save_weather_data(weather_data)
        return weather_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data for {city}: {e}")
        return f"Error fetching weather data for {city}: {e}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Unexpected error: {e}"

def fetch_weather_forecast(city: str):
    logger.info(f"Started fetching weather forecast data for city: {city}")
    try:
        api_key = settings.openweather_api_key
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        forecast_data = response.json()
        for entry in forecast_data['list']:
            weather_data = {
                'city': city,
                'main': entry['weather'][0]['main'],
                'temp': entry['main']['temp'] - 273.15,
                'feels_like': entry['main']['feels_like'] - 273.15,
                'humidity': entry['main']['humidity'],
                'wind_speed': entry['wind']['speed'],
                'dt': entry['dt']
            }
            save_weather_data(weather_data)
        logger.info(f"Weather forecast data fetched for {city}")
        return forecast_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather forecast data for {city}: {e}")
        return f"Error fetching weather forecast data for {city}: {e}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Unexpected error: {e}"

def start_scheduler():
    scheduler = BackgroundScheduler()
    cities = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]
    for city in cities:
        scheduler.add_job(fetch_weather_data, 'interval', minutes=5, args=[city])
        scheduler.add_job(fetch_weather_forecast, 'interval', hours=1, args=[city])
    scheduler.start()
