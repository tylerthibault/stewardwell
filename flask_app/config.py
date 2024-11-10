import os

class Config:
    # Get the absolute path to the project root directory
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Database configuration
    DB_NAME = 'app.db'
    DB_FOLDER = os.path.join(BASE_DIR, 'instance')
    
    # Create database directory if it doesn't exist
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        
    # Database URI
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DB_FOLDER, DB_NAME)}'
    
    # Flask configuration
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Print the database path for debugging
    print(f"Database path: {os.path.join(DB_FOLDER, DB_NAME)}")
