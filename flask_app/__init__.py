from flask import Flask
from config import Config
from flask_app.utils.logger import setup_logger
from flask_app.extensions import db, login_manager, migrate, bcrypt
import os

@login_manager.user_loader
def load_user(id):
    from flask_app.models import User
    return User.query.get(int(id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception as e:
        print(f"Error creating instance path: {e}")
    
    # Setup logger
    logger = setup_logger(app)
    if logger is None:
        print("Warning: Failed to initialize logger")
    else:
        app.logger = logger
    
    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints here
    from flask_app.controllers.main import main_bp
    from flask_app.controllers.auth import auth_bp
    from flask_app.controllers.admin import admin_bp
    from flask_app.controllers.family import family_bp
    from flask_app.controllers.settings import settings_bp
    from flask_app.controllers.rewards import rewards_bp
    from flask_app.controllers.goals import goals_bp
    from flask_app.controllers.chores import chores_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(chores_bp)
    
    # Register CLI commands
    from flask_app.commands import init_commands
    init_commands(app)
    
    return app