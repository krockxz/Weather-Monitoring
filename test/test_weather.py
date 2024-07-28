import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ensure the parent directory is in the sys.path to find main.py and other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import config
from app import crud
from app.scheduler import fetch_weather_data, start_scheduler

class TestWeatherSystem(unittest.TestCase):

    def setUp(self):
        self.api_key = "975159ed0282f7db912074d9984a0e95"
        self.location = "your_location"
        config.settings.openweather_api_key = self.api_key
        config.settings.location = self.location

    @patch('app.scheduler.requests.get')
    def test_system_setup(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = fetch_weather_data(self.location)
        self.assertTrue(response)
        mock_get.assert_called_once_with(
            f"http://api.openweathermap.org/data/2.5/weather?q={self.location}&appid={self.api_key}"
        )

    @patch('app.scheduler.requests.get')
    def test_data_retrieval(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "main": {"temp": 300.15, "feels_like": 298.15, "humidity": 80},
            "weather": [{"main": "Clear"}],
            "wind": {"speed": 3.5},
            "dt": 1625247600
        }
        mock_get.return_value = mock_response

        data = fetch_weather_data(self.location)
        self.assertEqual(data['temp'], 300.15 - 273.15)  # Adjusted to Celsius
        self.assertEqual(data['feels_like'], 298.15 - 273.15)  # Adjusted to Celsius
        self.assertEqual(data['main'], "Clear")
        self.assertEqual(data['humidity'], 80)
        self.assertEqual(data['wind_speed'], 3.5)

    def test_temperature_conversion(self):
        kelvin = 300.15
        celsius = kelvin - 273.15
        self.assertAlmostEqual(celsius, 27, places=1)

        fahrenheit = (kelvin - 273.15) * 9/5 + 32
        self.assertAlmostEqual(fahrenheit, 80.6, places=1)

    def test_daily_weather_summary(self):
        conn = crud.get_db_connection()
        with conn:
            conn.execute("DELETE FROM weather")
            conn.execute("INSERT INTO weather (city, main, temp, feels_like, humidity, wind_speed, dt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('TestCity1', 'Clear', 27.0, 25.0, 60, 3.0, 1625247600))
            conn.execute("INSERT INTO weather (city, main, temp, feels_like, humidity, wind_speed, dt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('TestCity2', 'Cloudy', 25.0, 24.0, 65, 2.5, 1625247600))
            conn.execute("INSERT INTO weather (city, main, temp, feels_like, humidity, wind_speed, dt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('TestCity3', 'Clear', 29.0, 28.0, 70, 4.0, 1625247600))
            conn.execute("INSERT INTO weather (city, main, temp, feels_like, humidity, wind_speed, dt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('TestCity4', 'Rain', 22.0, 21.0, 80, 5.0, 1625247600))
            conn.commit()

        summary = crud.get_daily_summary()
        expected_avg_temp = (27.0 + 25.0 + 29.0 + 22.0) / 4
        self.assertAlmostEqual(summary[0]['avg_temp'], 27.0, places=1)  # Match first city's avg temp
        self.assertEqual(summary[0]['max_temp'], 27.0)
        self.assertEqual(summary[0]['min_temp'], 27.0)
        self.assertEqual(summary[0]['dominant_condition'], "Clear")

    @patch('app.crud.send_email_alert')  # Mock email sending
    def test_alerting_thresholds(self, mock_send_email_alert):
        mock_send_email_alert.return_value = None  # Bypass email sending

        thresholds = {'temperature': 299, 'condition': 'Rain'}
        conn = crud.get_db_connection()
        with conn:
            conn.execute("DELETE FROM weather")
            conn.execute("DELETE FROM alerts")
            conn.execute("INSERT INTO weather (city, main, temp, feels_like, humidity, wind_speed, dt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('TestCity', 'Rain', 305, 300, 80, 5.0, 1625247600))  # Ensure temp is above threshold
            conn.commit()

        crud.check_alert_thresholds(thresholds['temperature'], thresholds['condition'])
        alerts = crud.fetch_alerts()

        self.assertTrue(any(alert['temp_threshold'] == thresholds['temperature'] for alert in alerts))
        self.assertFalse(any(alert['condition'] != thresholds['condition'] for alert in alerts))

if __name__ == '__main__':
    unittest.main()
