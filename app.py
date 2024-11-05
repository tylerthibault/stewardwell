from flask_app import app, db
from flask_app.controllers import routes, user, family, budget, chores

# Create tables
with app.app_context():
    db.create_all()

# keep this at the bottom of this file!!
if __name__=="__main__":	 
    app.run(
        host='0.0.0.0',  # Allows external connections
        port=5000,       # Specify port
        debug=True,      # Keep debug mode
        threaded=True    # Enable threading for better performance
    )	