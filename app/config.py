from dotenv import load_dotenv
import os

load_dotenv() 

class Settings:
    openweather_api_key = os.getenv("OPENWEATHER_API_KEY")
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")

settings = Settings()
