import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration - MySQL Workbench
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'ROOT'
    MYSQL_DATABASE = 'agridb'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    
    # API Keys
    WEATHER_API_KEY = "8ec8aac1ced747ec89655941252409"
    GEMINI_API_KEY = "AIzaSyBIA0VRcgOtGImuIa2HSIaAcLAyxM6UYM4"
    MARKET_API_KEY = "579b464db66ec23bdd000001b19bb12224e0498057c7f90da667557f"
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
