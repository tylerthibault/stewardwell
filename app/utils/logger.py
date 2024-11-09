import os
import json
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from flask import request, has_request_context, current_app
import traceback

class JSONFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        
    def format(self, record):
        # Create the base log object
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        
        # Add request information if available
        if has_request_context():
            log_obj.update({
                "method": request.method,
                "url": request.url,
                "ip": request.remote_addr,
                "user_agent": str(request.user_agent)
            })
            
            # Add user information if authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                log_obj.update({
                    "user_id": request.user.id,
                    "username": request.user.username
                })
        
        # Add exception information if present
        if record.exc_info:
            log_obj["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "stacktrace": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if any
        if hasattr(record, "extra_fields"):
            log_obj.update(record.extra_fields)
        
        return json.dumps(log_obj)

def setup_logger(app):
    """Setup the application logger"""
    
    # Create logs directory if it doesn't exist
    # Changed to use absolute path from project root
    project_root = os.path.abspath(os.path.join(app.root_path, '..'))
    logs_dir = os.path.join(project_root, 'logs')
    
    try:
        os.makedirs(logs_dir, exist_ok=True)
        print(f"Logs directory created/verified at: {logs_dir}")  # Debug print
    except Exception as e:
        print(f"Error creating logs directory: {e}")  # Debug print
        return None
    
    # Create the logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Create a daily rotating file handler
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(logs_dir, f'app_{today}.log')
    
    try:
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days of logs
            encoding='utf-8'
        )
        print(f"Log file created at: {log_file}")  # Debug print
        
        # Set the formatter
        file_handler.setFormatter(JSONFormatter())
        
        # Add the handler to the logger
        logger.addHandler(file_handler)
        
        # If in development, also log to console with more detailed formatting
        if app.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(JSONFormatter())
            logger.addHandler(console_handler)
        
        # Test log entry
        logger.info("Logging system initialized successfully",
                   extra={"log_file": log_file, "log_dir": logs_dir})
        
        return logger
        
    except Exception as e:
        print(f"Error setting up file handler: {e}")  # Debug print
        return None

def get_logger():
    """Get the application logger"""
    return logging.getLogger('app')