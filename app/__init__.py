import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def make_celery(app_name=__name__):
    """Create and configure Celery instance"""
    # Try different Redis configurations
    redis_configs = [
        'redis://127.0.0.1:6379/0',
        'redis://0.0.0.0:6379/0',
        os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    ]
    
    redis_url = redis_configs[0]  # Default to localhost
    
    celery = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url,
        include=['app.core.reporter']
    )
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        result_expires=3600,
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
    )
    
    return celery

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configuration
    app.secret_key = os.getenv("SESSION_SECRET", "dev-secret-key")
    
    # Database configuration
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'db.sqlite')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from app.api.reports import reports_bp
    app.register_blueprint(reports_bp)
    
    # # Create tables
    # with app.app_context():
    #     # Import models to ensure they are registered
    #     from app.models import db_models
    #     db.create_all()
        
    #     # Load initial data
    #     from app.core.data_loader import load_data
    #     try:
    #         load_data()
    #         logging.info("Data loaded successfully")
    #     except Exception as e:
    #         logging.error(f"Failed to load data: {e}")
    
    return app

# Create Celery instance
celery = make_celery()
