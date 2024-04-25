# from flask import app
class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'  # Path to the SQLite database file
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disabling modification tracking for performance and to avoid warnings
    
    # Additional configuration options
    # You can add more configuration options here as needed
    SECRET_KEY = 'c285fbd3dc01b58fa5f8c09b367ef58a'