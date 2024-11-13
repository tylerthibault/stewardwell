from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from config import Config
from app.utils.logger import setup_logger
import logging

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

    # Set up logging
    logger = setup_logger(app)

    # Import models to ensure they're known to Flask-Migrate
    from app.models.user import User, Family
    from app.modules.homeconomy.models import Chore, CompletedChore, Reward, ClaimedReward, Goal

    @app.before_request
    def before_request():
        # Add user info to request for logging
        if current_user.is_authenticated:
            request.user_id = current_user.id
            g.user_id = current_user.id
            if hasattr(current_user, 'user_type'):
                request.user_type = current_user.user_type
                g.user_type = current_user.user_type
        else:
            request.user_id = None
            g.user_id = None
            request.user_type = None
            g.user_type = None

        # Log request
        logger.info(f"Request: {request.method} {request.url}",
                   extra={
                       'user_id': getattr(request, 'user_id', None),
                       'user_type': getattr(request, 'user_type', None),
                       'remote_addr': request.remote_addr,
                       'user_agent': str(request.user_agent)
                   })

    @app.after_request
    def after_request(response):
        # Log response
        logger.info(f"Response: {response.status}",
                   extra={
                       'user_id': getattr(request, 'user_id', None),
                       'user_type': getattr(request, 'user_type', None),
                       'remote_addr': request.remote_addr,
                       'status_code': response.status_code
                   })
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log unhandled exceptions
        logger.error(f"Unhandled exception: {str(e)}",
                    extra={
                        'user_id': getattr(request, 'user_id', None),
                        'user_type': getattr(request, 'user_type', None),
                        'remote_addr': request.remote_addr,
                        'exception_type': type(e).__name__
                    },
                    exc_info=True)
        # Re-raise the exception after logging
        raise e

    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.modules.homeconomy import bp as homeconomy_bp
    app.register_blueprint(homeconomy_bp)

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.context_processor
    def utility_processor():
        return {
            'User': User,
            'CompletedChore': CompletedChore
        }

    # Log application startup
    logger.info("Application started successfully", 
                extra={
                    'config': {k: str(v) for k, v in app.config.items() 
                             if not k.startswith('_') and k not in ['SECRET_KEY']}
                })

    return app
