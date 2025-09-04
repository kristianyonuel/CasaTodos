"""
Configuration settings for La Casa de Todos NFL Fantasy League
"""
import os
from datetime import datetime

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nfl-fantasy-super-secret-key-2024'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'nfl_fantasy.db')
    
    # League Configuration
    CURRENT_SEASON = int(os.environ.get('NFL_SEASON', datetime.now().year))
    WEEKLY_FEE = float(os.environ.get('WEEKLY_FEE', 5.0))
    SEASON_FEE = float(os.environ.get('SEASON_FEE', 10.0))
    
    # NFL API Configuration
    ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    API_TIMEOUT = 15
    
    # Timezone Configuration
    TIMEZONE = 'America/Puerto_Rico'  # AST
    
    # Admin Configuration
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin123'
    
    # Application Configuration
    ITEMS_PER_PAGE = 20
    MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'nfl_fantasy.log'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'

class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
