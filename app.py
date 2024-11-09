from flask_app import create_app, db
from app.models.user import User, Family, FamilyGoal, FamilyJoinRequest
import os
import atexit
from app.seed import seed_database

app = create_app()

def init_db():
    with app.app_context():
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Created data directory at {data_dir}")

        db_path = os.path.join(data_dir, 'app.db')
        
        # Only create tables if database doesn't exist
        if not os.path.exists(db_path):
            print("Database not found. Creating new database...")
            db.create_all()
            # Seed the database with initial data
            seed_database()
            print("Database initialized and seeded successfully!")
        else:
            print("Database exists. Checking for missing tables...")
            # This will create any missing tables
            db.create_all()
            print("Database schema updated.")
            
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")

def cleanup():
    # Properly close the database connection
    if db.session:
        db.session.remove()
    if db.engine:
        db.engine.dispose()

# Register the cleanup function to run on exit
atexit.register(cleanup)

if __name__ == '__main__':
    init_db()  # Initialize database only if it doesn't exist
    app.run(debug=True)
