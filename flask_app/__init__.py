from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "shhhhhhhhhhhhhhhhhhhhhhh"
app.config.from_object('flask_app.config.connection')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# Import models after db initialization to avoid circular imports
from flask_app.models import (
    users, 
    families, 
    family_members,
    chores,
    chore_assignments,
    rewards,
    reward_redemptions,
    budgets, 
    budget_categories, 
    transactions
)

# Import routes after models
from flask_app.controllers import routes, user, family, budget, chores

