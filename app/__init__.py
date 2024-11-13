from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Import models to ensure they're known to Flask-Migrate
    from app.models.user import User, Family
    from app.modules.homeconomy.models import Chore, CompletedChore, Reward, ClaimedReward, Goal

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.modules.homeconomy import bp as homeconomy_bp
    app.register_blueprint(homeconomy_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.context_processor
    def utility_processor():
        return {
            'User': User,  # Make User model available in templates
            'CompletedChore': CompletedChore  # Make CompletedChore model available in templates
        }

    return app
