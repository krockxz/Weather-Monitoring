import sqlite3

def init_db():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        main TEXT,
        temp REAL,
        feels_like REAL,
        dt TEXT
    )
    ''')
    conn.commit()
    conn.close()

def save_weather_data(city, main, temp, feels_like, dt):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO weather_data (city, main, temp, feels_like, dt)
    VALUES (?, ?, ?, ?, ?)
    ''', (city, main, temp, feels_like, dt))
    conn.commit()
    conn.close()

def get_daily_summary():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT city, main, AVG(temp) as avg_temp, MAX(temp) as max_temp, MIN(temp) as min_temp, dt
    FROM weather_data
    GROUP BY city, DATE(dt)
    ''')
    result = cursor.fetchall()
    conn.close()
    return result
