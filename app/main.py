from fastapi import FastAPI, HTTPException
from .scheduler import start_scheduler, fetch_weather_data
from .crud import create_tables, get_daily_summary, check_alert_thresholds, save_weather_data, fetch_alerts, clear_all_alerts
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

create_tables()
logger.info("Starting up the Weather Data Processing System")
start_scheduler()

@app.get("/")
def read_root():
    return {"message": "Weather Data Processing System"}

@app.get("/fetch-weather/{city}")
def fetch_weather(city: str):
    logger.info(f"Fetching weather data for city: {city}")
    weather_data = fetch_weather_data(city)
    if "Error" in weather_data:
        raise HTTPException(status_code=500, detail=weather_data)
    save_weather_data(weather_data)
    return weather_data

@app.get("/weather-summary/")
def weather_summary():
    logger.info("Fetching daily weather summary")
    start_time = time.time()
    summary = get_daily_summary()
    elapsed_time = time.time() - start_time
    logger.info(f"Fetched daily weather summary in {elapsed_time:.2f} seconds")
    if not summary:
        logger.warning("No weather data found for summary")
    return {"daily_summary": summary}

@app.post("/set-threshold/")
def set_threshold(city: str, condition: str, temp_threshold: float):
    logger.info(f"Setting alert threshold for {city}: {condition} at {temp_threshold}°C")
    check_alert_thresholds(city, temp_threshold, condition)
    return {"status": "Threshold set and checked"}

@app.get("/alerts/")
def get_alerts():
    logger.info("Fetching alerts")
    alerts = fetch_alerts()
    return {"alerts": alerts}

@app.delete("/clear-alerts/")
def clear_alerts():
    try:
        logger.info("Clearing all alerts")
        success = clear_all_alerts()
        if not success:
            raise HTTPException(status_code=500, detail="Error clearing alerts")
        return {"status": "success", "message": "All alerts cleared"}
    except Exception as e:
        logger.error(f"Error clearing alerts: {e}")
        raise HTTPException(status_code=500, detail="Error clearing alerts")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
