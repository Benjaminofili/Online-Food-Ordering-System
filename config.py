import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    db_url = os.environ.get('DATABASE_URL')
    # Render provides 'postgres://' but SQLAlchemy requires 'postgresql://'
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cloudinary config (will be used later)
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')