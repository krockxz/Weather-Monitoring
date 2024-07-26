```markdown
# Weather Data Processing System

## Overview
The Weather Data Processing System is a FastAPI application that fetches, stores, and processes weather data. It includes a scheduler for periodic data fetching, CRUD operations, and alert management based on weather conditions.

## Project Structure
```
weather/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── crud.py
│   ├── main.py
│   ├── models.py
│   ├── scheduler.py
│   ├── test_weather.py
├── venv/
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
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
- **venv/**: Virtual environment directory.
- **.env**: Environment variables file.
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **docker-compose.yml**: Docker Compose configuration file.
- **Dockerfile**: Dockerfile for containerizing the application.
- **README.md**: Project documentation.
- **requirements.txt**: Python dependencies.
- **streamlit_app.py**: Streamlit application entry point.
- **weather.db**: SQLite database file.

## Installation

### Prerequisites
- Python 3.8+
- Docker (optional, for containerization)

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
   OPENWEATHER_API_KEY=your_openweather_api_key
   EMAIL_USER=your_email
   EMAIL_PASSWORD=your_email_password
   ```

5. Initialize the database:
   ```sh
   python -m app.main
   ```

6. Run the FastAPI server:
   ```sh
   uvicorn app.main:app --reload
   ```

7. Access the API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Docker Setup (Optional)

1. Build the Docker image:
   ```sh
   docker build -t weather-app .
   ```

2. Run the Docker container:
   ```sh
   docker run -d -p 8000:8000 --env-file .env weather-app
   ```

## Usage

### API Endpoints

- **GET /**: Welcome message
- **GET /fetch-weather/{city}**: Fetch weather data for a specific city
- **GET /weather-summary/**: Get the daily weather summary
- **POST /set-threshold/**: Set alert thresholds
  - Parameters:
    - `city`: City name
    - `condition`: Weather condition (e.g., "Clear", "Rain")
    - `temp_threshold`: Temperature threshold for alerts
- **GET /alerts/**: Retrieve weather alerts

### Running Tests

Run the unit tests using:
```sh
python -m unittest app.test_weather
```
