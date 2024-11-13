import os
from datetime import timedelta

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///stewardwell.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Logging configuration
    LOG_DIR = 'logs'
    LOG_FILENAME = 'stewardwell.log'
    ERROR_LOG_FILENAME = 'error.log'
    AUDIT_LOG_FILENAME = 'audit.log'
    ACCESS_LOG_FILENAME = 'access.log'
    
    # Log file paths
    LOG_PATH = os.path.join(LOG_DIR, LOG_FILENAME)
    ERROR_LOG_PATH = os.path.join(LOG_DIR, ERROR_LOG_FILENAME)
    AUDIT_LOG_PATH = os.path.join(LOG_DIR, AUDIT_LOG_FILENAME)
    ACCESS_LOG_PATH = os.path.join(LOG_DIR, ACCESS_LOG_FILENAME)
    
    # Log settings
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Log levels for different components
    LOG_LEVEL = 'INFO'
    ERROR_LOG_LEVEL = 'ERROR'
    AUDIT_LOG_LEVEL = 'INFO'
    ACCESS_LOG_LEVEL = 'INFO'
    
    # Module-specific log settings
    MODULE_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(user_id)s] - %(message)s'
    
    # Security logging settings
    SECURITY_LOG_FORMAT = '%(asctime)s - SECURITY - %(levelname)s - [%(user_id)s] - %(message)s'
    SECURITY_LOG_FILENAME = 'security.log'
    SECURITY_LOG_PATH = os.path.join(LOG_DIR, SECURITY_LOG_FILENAME)
    
    # Performance logging settings
    PERFORMANCE_LOG_FORMAT = '%(asctime)s - PERFORMANCE - %(levelname)s - %(message)s'
    PERFORMANCE_LOG_FILENAME = 'performance.log'
    PERFORMANCE_LOG_PATH = os.path.join(LOG_DIR, PERFORMANCE_LOG_FILENAME)
    
    @staticmethod
    def init_app(app):
        # Create logs directory if it doesn't exist
        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)
        
        # Create log files if they don't exist
        log_files = [
            Config.LOG_PATH,
            Config.ERROR_LOG_PATH,
            Config.AUDIT_LOG_PATH,
            Config.ACCESS_LOG_PATH,
            Config.SECURITY_LOG_PATH,
            Config.PERFORMANCE_LOG_PATH
        ]
        
        for log_file in log_files:
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write('')

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = True  # Log SQL queries

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'INFO'
    SQLALCHEMY_ECHO = False
    
    # Override these in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or None
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production logging setup
        import logging
        from logging.handlers import SMTPHandler
        
        # Email error logs to admins
        credentials = None
        secure = None
        
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
                
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.ADMIN_EMAIL],
            subject='StewardWell Application Error',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class TestingConfig(Config):
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
