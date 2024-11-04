import os
from pathlib import Path

# Create instance folder if it doesn't exist
instance_path = Path(__file__).parent.parent.parent / 'instance'
instance_path.mkdir(exist_ok=True)

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(instance_path / 'stewardwell.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Session configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'shhhhhhhhhhhhhhhhhhhhhhh')
