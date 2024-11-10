import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_app.config import Config
from flask_app.utils.logger import setup_logger

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Setup logger
logger = setup_logger()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from flask_app.controllers.landing_controller import landing_bp
    app.register_blueprint(landing_bp)
    
    from flask_app.controllers.example_controller import example_bp
    app.register_blueprint(example_bp)

    from flask_app.modules.homeconomy.controllers import homeconomy_bp
    app.register_blueprint(homeconomy_bp)

    from flask_app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    # Create database tables
    with app.app_context():
        try:
            # Ensure the database directory exists
            db_path = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            
            # Create tables
            db.create_all()
            logger.info(f"Database initialized at {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Database path: {app.config['SQLALCHEMY_DATABASE_URI']}")
            raise

    @login_manager.user_loader
    def load_user(id):
        from flask_app.models.user import User
        return User.query.get(int(id))

    return app
