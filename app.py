from flask_app import create_app, db
from flask_app.models.user import User, Family, FamilyGoal, FamilyJoinRequest
from flask_app.seed import seed_database
import os
import atexit

app = create_app()

def init_db():
    with app.app_context():
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            print(f"Created data directory at {data_dir}")

            db_path = os.path.join(data_dir, 'app.db')
            
            if not os.path.exists(db_path):
                print("Database not found. Creating new database...")
                db.create_all()
                seed_database()
                print("Database initialized and seeded successfully!")
            else:
                print("Database exists. Checking for missing tables...")
                db.create_all()
                print("Database schema updated.")
                
            print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

def cleanup():
    try:
        with app.app_context():
            if db.session:
                db.session.remove()
            if db.engine:
                db.engine.dispose()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

# Register the cleanup function to run on exit
atexit.register(cleanup)

if __name__ == '__main__':
    init_db()  # Initialize database only if it doesn't exist
    app.run(debug=True)
