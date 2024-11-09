from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from flask_app.utils.logger import setup_logger
import os

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

@login_manager.user_loader
def load_user(id):
    from flask_app.models.user import User
    return User.query.get(int(id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
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
    from flask_app.controllers.chores import chores_bp
    from flask_app.controllers.rewards import rewards_bp
    from flask_app.controllers.goals import goals_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(chores_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(goals_bp)
    
    # Register CLI commands
    from flask_app.commands import init_commands
    init_commands(app)
    
<<<<<<< HEAD:flask_app/__init__.py
    # Add context processor for module settings
    @app.context_processor
    def inject_module_settings():
        if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
            return {'module_settings': {}}
            
        # Import ModuleSettings here to avoid circular import
        from flask_app.models.user import ModuleSettings
        
        settings = ModuleSettings.query.filter_by(family_id=current_user.family_id).all()
        module_settings = {
            setting.module_name: setting.is_enabled 
            for setting in settings
        }
        return {'module_settings': module_settings}
    
=======
>>>>>>> parent of 83ed391 (fixed minor bugs like kids not being able to complete chores):app/__init__.py
    return app 