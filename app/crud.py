import sqlite3
import logging
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_db_connection():
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    main TEXT NOT NULL,
                    temp REAL NOT NULL,
                    feels_like REAL NOT NULL,
                    humidity INTEGER NOT NULL,
                    wind_speed REAL NOT NULL,
                    dt INTEGER NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    date TEXT NOT NULL,
                    avg_temp REAL NOT NULL,
                    max_temp REAL NOT NULL,
                    min_temp REAL NOT NULL,
                    avg_humidity REAL NOT NULL,
                    avg_wind_speed REAL NOT NULL,
                    dominant_condition TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    condition TEXT NOT NULL,
                    temp_threshold REAL NOT NULL,
                    alert_time TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

def save_weather_data(weather_data):
    try:
        logger.info(f"Attempting to save weather data: {weather_data}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO weather (city, main, temp, feels_like, humidity, wind_speed, dt)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (weather_data['city'], weather_data['main'], round(weather_data['temp'], 2),
                  round(weather_data['feels_like'], 2), weather_data['humidity'], 
                  weather_data.get('wind_speed', 0), weather_data['dt']))
            conn.commit()
            logger.info(f"Weather data saved for {weather_data['city']}: {weather_data}")
    except Exception as e:
        logger.error(f"Error saving weather data: {e}")

def get_daily_summary():
    try:
        logger.info("Retrieving daily summary")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city, date(dt, 'unixepoch') as date, AVG(temp) as avg_temp, MAX(temp) as max_temp, MIN(temp) as min_temp, AVG(humidity) as avg_humidity, AVG(wind_speed) as avg_wind_speed, main
                FROM weather
                GROUP BY city, date(dt, 'unixepoch'), main
            ''')
            result = cursor.fetchall()
            daily_summary = []
            for row in result:
                dominant_condition = row['main']
                daily_summary.append({
                    'city': row['city'],
                    'date': row['date'],
                    'avg_temp': round(row['avg_temp'], 2),
                    'max_temp': round(row['max_temp'], 2),
                    'min_temp': round(row['min_temp'], 2),
                    'avg_humidity': round(row['avg_humidity'], 2),
                    'avg_wind_speed': round(row['avg_wind_speed'], 2),
                    'dominant_condition': dominant_condition
                })
            save_daily_summary(daily_summary)
            logger.info(f"Daily summary retrieved and saved: {daily_summary}")
            return daily_summary
    except Exception as e:
        logger.error(f"Error retrieving daily summary: {e}")
        return []

def save_daily_summary(daily_summary):
    try:
        logger.info(f"Attempting to save daily summary: {daily_summary}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for summary in daily_summary:
                cursor.execute("""
                    INSERT INTO daily_summary (city, date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_condition)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (summary['city'], summary['date'], summary['avg_temp'],
                      summary['max_temp'], summary['min_temp'], summary['avg_humidity'], summary['avg_wind_speed'], summary['dominant_condition']))
            conn.commit()
            logger.info(f"Daily summary saved")
    except Exception as e:
        logger.error(f"Error saving daily summary: {e}")

def check_alert_thresholds(city, temp_threshold, condition):
    try:
        logger.info(f"Checking alert thresholds for city: {city} with condition: {condition} and threshold: {temp_threshold}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city, temp, dt
                FROM weather
                WHERE temp > ? AND main = ? AND city = ?
            ''', (temp_threshold, condition, city))
            alerts = cursor.fetchall()
            for alert in alerts:
                alert_time = int(alert['dt'])
                # Check if alert already exists
                cursor.execute("""
                    SELECT * FROM alerts
                    WHERE city = ? AND condition = ? AND temp_threshold = ? AND alert_time = ?
                """, (city, condition, temp_threshold, alert_time))
                existing_alert = cursor.fetchone()
                if not existing_alert:
                    cursor.execute("""
                        INSERT INTO alerts (city, condition, temp_threshold, alert_time)
                        VALUES (?, ?, ?, ?)
                    """, (city, condition, temp_threshold, alert_time))
            conn.commit()
            logger.info(f"Alerts checked and saved for city: {city} if any")
    except Exception as e:
        logger.error(f"Error checking alert thresholds: {e}")


def fetch_alerts():
    try:
        logger.info("Fetching alerts")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts')
            alerts = cursor.fetchall()
            logger.info(f"Alerts retrieved: {alerts}")
            return [dict(alert) for alert in alerts]
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return []
    
def clear_all_alerts():
    try:
        logger.info("Clearing all alerts")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM alerts')
            conn.commit()
            logger.info("All alerts cleared")
    except Exception as e:
        logger.error(f"Error clearing alerts: {e}")
        return False
    return True

