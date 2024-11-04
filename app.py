from flask_app import app, db
from flask_app.controllers import routes, user, family, budget, chores

# Create tables
with app.app_context():
    db.create_all()

# keep this at the bottom of this file!!
if __name__=="__main__":	 
    app.run(debug=True)	