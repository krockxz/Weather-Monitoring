import sqlite3
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from .config import settings  # Ensure settings are imported

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
                INSERT INTO weather (city, main, temp, feels_like, dt)
                VALUES (?, ?, ?, ?, ?)
            """, (weather_data['city'], weather_data['main'], round(weather_data['temp'], 2),
                  round(weather_data['feels_like'], 2), weather_data['dt']))
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
                SELECT city, date(dt, 'unixepoch') as date, AVG(temp) as avg_temp, MAX(temp) as max_temp, MIN(temp) as min_temp, main
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
                    INSERT INTO daily_summary (city, date, avg_temp, max_temp, min_temp, dominant_condition)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (summary['city'], summary['date'], summary['avg_temp'],
                      summary['max_temp'], summary['min_temp'], summary['dominant_condition']))
            conn.commit()
            logger.info(f"Daily summary saved")
    except Exception as e:
        logger.error(f"Error saving daily summary: {e}")

def send_email_alert(city, condition, temp_threshold, alert_time):
    try:
        alert_datetime = datetime.utcfromtimestamp(alert_time).strftime('%Y-%m-%d %H:%M:%S')
        msg = MIMEText(f"Alert! The temperature in {city} exceeded {temp_threshold}°C with condition {condition} at {alert_datetime}")
        msg['Subject'] = f"Weather Alert for {city}"
        msg['From'] = settings.email_user
        msg['To'] = "recipient_email@example.com"  # Add the recipient's email address

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(settings.email_user, settings.email_password)
            server.send_message(msg)
        logger.info(f"Alert email sent for {city}")
    except Exception as e:
        logger.error(f"Error sending email alert: {e}")

def check_alert_thresholds(temp_threshold, condition):
    try:
        logger.info("Checking alert thresholds")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city, temp, dt
                FROM weather
                WHERE temp > ? AND main = ?
            ''', (temp_threshold, condition))
            alerts = cursor.fetchall()
            for alert in alerts:
                alert_time = int(alert['dt'])
                cursor.execute("""
                    INSERT INTO alerts (city, condition, temp_threshold, alert_time)
                    VALUES (?, ?, ?, ?)
                """, (alert['city'], condition, temp_threshold, alert_time))
                send_email_alert(alert['city'], condition, temp_threshold, alert_time)
            conn.commit()
            logger.info(f"Alerts checked and saved if any")
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
