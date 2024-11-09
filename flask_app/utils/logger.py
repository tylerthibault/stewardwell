import logging
import json
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

def get_logger():
    return logging.getLogger('flask_app')

def setup_logger(app):
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('flask_app')
    logger.setLevel(logging.DEBUG)
    
    # Create handlers
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y-%m-%d")}.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatters and add it to handlers
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                'timestamp': self.formatTime(record, self.datefmt),
                'level': record.levelname,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage()
            }
            
            # Add extra fields if they exist
            if hasattr(record, 'extra'):
                log_record.update(record.extra)
                
            return json.dumps(log_record)
    
    file_handler.setFormatter(JsonFormatter())
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    
    return logger