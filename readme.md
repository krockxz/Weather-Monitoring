
# Weather Data Processing System

## Overview
The Weather Data Processing System is a FastAPI application that fetches, stores, and processes weather data. It includes a scheduler for periodic data fetching, CRUD operations, and alert management based on weather conditions.

## Project Structure
```markdown
weather/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── crud.py
│   ├── main.py
│   ├── models.py
│   ├── scheduler.py
│   ├── test_weather.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── streamlit_app.py
├── weather.db
```

### Description of Files
- **app/**: Contains all the application-specific modules and packages.
  - `__init__.py`: Marks the directory as a Python package.
  - `config.py`: Configuration settings for the application.
  - `crud.py`: CRUD operations for the application.
  - `main.py`: The main entry point for the FastAPI application.
  - `models.py`: Database models and schema definitions.
  - `scheduler.py`: Scheduler-related functions.
  - `test_weather.py`: Unit tests for the application.
- **.env**: Environment variables file.
- **requirements.txt**: Python dependencies.
- **streamlit_app.py**: Streamlit application entry point.
- **weather.db**: SQLite database file.

## Installation

### Prerequisites
- Python 3.8+

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/weather.git
   cd weather
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file and add your environment variables:
   ```
   OPENWEATHER_API_KEY=975159ed0282f7db912074d9984a0e95
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASSWORD=your_email_password
   ```

5. Start UI:
   ```sh
   streamlit run streamlit_app.py
   ```

6. Run the FastAPI server:
   ```sh
   uvicorn app.main:app --reload
   ```
   
7. Run the tests after testing all the APIs:
   ```sh
   python -m unittest test.test_weather
   ```

## Usage

### API Endpoints

- **GET /fetch-weather/{city}**: Fetch weather data for a specific city
   ```sh
   curl -X 'GET' \
     'http://127.0.0.1:8000/fetch-weather/Delhi' \
     -H 'accept: application/json'
   ```
- **GET /weather-summary/**: Get the daily weather summary
   ```sh
   curl -X 'GET' \
     'http://127.0.0.1:8000/weather-summary/' \
     -H 'accept: application/json'
   ```
   This saves the fetched weather summary from the earlier API and also updates and stores the weather summary in 5mins

- **POST /set-threshold/**: Set alert thresholds
   - Parameters:
     - `city`: City name
     - `condition`: Weather condition (e.g., "Clear", "Rain")
     - `temp_threshold`: Temperature threshold for alerts
   ```sh
   curl -X 'POST' \
     'http://127.0.0.1:8000/set-threshold/' \
     -H 'accept: application/json' \
     -d '{
       "city": "Delhi",
       "condition": "Clear",
       "temp_threshold": 35.0
     }'
   ```
- **GET /alerts/**: Retrieve weather alerts
   ```sh
   curl -X 'GET' \
     'http://127.0.0.1:8000/alerts/' \
     -H 'accept: application/json'
   ```
### Data Flow Diagram Description

#### Context Level (Level 0)

**Entities:**
1. **User**
   - Interacts with the system through the FastAPI endpoints.
2. **OpenWeatherMap API**
   - Provides weather data.

**Processes:**
1. **Weather Data Processing System**
   - Fetches weather data from OpenWeatherMap API.
   - Stores weather data in the database.
   - Processes data for summaries and alerts.
   - Provides weather data and summaries to the user.
   - Sends alerts to the user based on thresholds.

**Data Stores:**
1. **Weather Database**
   - Stores raw weather data.
   - Stores daily weather summaries.
   - Stores alert configurations and triggered alerts.

**Data Flow:**
1. **User -> Weather Data Processing System:**
   - API requests (fetch weather, set thresholds, get summaries, get alerts).
2. **Weather Data Processing System -> User:**
   - API responses (weather data, summaries, alerts).
3. **Weather Data Processing System -> OpenWeatherMap API:**
   - API requests (fetch weather data).
4. **OpenWeatherMap API -> Weather Data Processing System:**
   - API responses (weather data).
5. **Weather Data Processing System -> Weather Database:**
   - Store raw weather data.
   - Store daily summaries.
   - Store alert configurations and triggered alerts.
6. **Weather Database -> Weather Data Processing System:**
   - Retrieve raw weather data.
   - Retrieve daily summaries.
   - Retrieve alert configurations and triggered alerts.

### Data Flow Diagram Details

#### Level 1 DFD

**Process 1: Fetch Weather Data**
- **Inputs:**
  - Request from the scheduler to OpenWeatherMap API.
- **Outputs:**
  - Weather data from OpenWeatherMap API to the system.
- **Stores:**
  - Raw weather data stored in the Weather Database.

**Process 2: Store Weather Data**
- **Inputs:**
  - Raw weather data from OpenWeatherMap API.
- **Outputs:**
  - Weather data saved in the Weather Database.

**Process 3: Generate Daily Summary**
- **Inputs:**
  - Raw weather data from the Weather Database.
- **Outputs:**
  - Daily summaries saved in the Weather Database.
- **Stores:**
  - Daily summaries stored in the Weather Database.

**Process 4: Set Alert Thresholds**
- **Inputs:**
  - User inputs (city, condition, temp_threshold).
- **Outputs:**
  - Alert thresholds stored in the Weather Database.
- **Stores:**
  - Alert configurations stored in the Weather Database.

**Process 5: Check Alert Thresholds**
- **Inputs:**
  - Raw weather data from the Weather Database.
  - Alert thresholds from the Weather Database.
- **Outputs:**
  - Triggered alerts.
  - Alert notifications sent to the user.
- **Stores:**
  - Triggered alerts stored in the Weather Database.

**Process 6: Retrieve Summaries and Alerts**
- **Inputs:**
  - User requests for summaries and alerts.
- **Outputs:**
  - Daily summaries and alerts retrieved from the Weather Database.
  - Responses sent to the user.

### Sample Visual Representation

You can visualize the above description using a tool like Draw.io. Here’s a step-by-step guide to creating the DFD:

1. **Context Level (Level 0) DFD:**
   - Create a central process labeled "Weather Data Processing System".
   - Draw arrows from "User" to the central process for input and from the process back to "User" for output.
   - Draw arrows from the central process to "OpenWeatherMap API" for input and from the API back to the process for output.
   - Draw arrows from the central process to "Weather Database" for storing and retrieving data.

2. **Level 1 DFD:**
   - Break down the central process into sub-processes: Fetch Weather Data, Store Weather Data, Generate Daily Summary, Set Alert Thresholds, Check Alert Thresholds, Retrieve Summaries and Alerts.
   - Connect each sub-process with appropriate data stores and external entities.
   - Ensure data flows are clearly labeled between processes, data stores, and external entities.
