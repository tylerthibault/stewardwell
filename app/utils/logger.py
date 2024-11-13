import logging
import logging.handlers
import os
from datetime import datetime
from functools import wraps
import traceback
import json
from flask import request, has_request_context, current_app

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            if hasattr(request, 'user_id'):
                record.user_id = request.user_id
            else:
                record.user_id = 'Anonymous'
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.user_id = None
            
        return super().format(record)

def setup_logger(app):
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create formatters
    console_formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    file_formatter = RequestFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(user_id)s - %(url)s - %(remote_addr)s - %(method)s - %(message)s'
    )

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Rotating file handler for general logs
    general_handler = logging.handlers.RotatingFileHandler(
        'logs/stewardwell.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    general_handler.setFormatter(file_formatter)
    general_handler.setLevel(logging.INFO)

    # Rotating file handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/error.log',
        maxBytes=10000000,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)

    # Create logger
    logger = logging.getLogger('stewardwell')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers if any
    logger.handlers = []
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(general_handler)
    logger.addHandler(error_handler)

    # Set Flask logger to use our handlers
    app.logger.handlers = logger.handlers

    return logger

def log_action(action_type):
    """
    Decorator to log actions with detailed information
    Usage: @log_action('user_login')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger = logging.getLogger('stewardwell')
            
            # Prepare context information
            context = {
                'action_type': action_type,
                'function': f.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            }
            
            if has_request_context():
                context.update({
                    'url': request.url,
                    'method': request.method,
                    'remote_addr': request.remote_addr,
                    'user_agent': str(request.user_agent)
                })
            
            try:
                # Log the start of the action
                logger.info(f"Starting {action_type}", extra={'context': context})
                
                # Execute the function
                result = f(*args, **kwargs)
                
                # Log successful completion
                logger.info(f"Completed {action_type} successfully", extra={'context': context})
                
                return result
                
            except Exception as e:
                # Log the error with traceback
                error_context = context.copy()
                error_context['error'] = str(e)
                error_context['traceback'] = traceback.format_exc()
                logger.error(f"Error in {action_type}: {str(e)}", 
                           extra={'context': error_context})
                raise
                
        return decorated_function
    return decorator

class ActivityLogger:
    """
    Class to handle activity logging for specific modules
    Usage: activity_logger = ActivityLogger('homeconomy')
    """
    def __init__(self, module_name):
        self.logger = logging.getLogger(f'stewardwell.{module_name}')
        self.module_name = module_name

    def log_activity(self, user_id, action, details=None, level=logging.INFO):
        """
        Log a user activity
        """
        activity = {
            'timestamp': datetime.utcnow().isoformat(),
            'module': self.module_name,
            'user_id': user_id,
            'action': action,
            'details': details or {}
        }

        if has_request_context():
            activity.update({
                'ip_address': request.remote_addr,
                'user_agent': str(request.user_agent)
            })

        self.logger.log(level, json.dumps(activity))

    def log_chore_completion(self, user_id, chore_id, chore_name):
        self.log_activity(
            user_id=user_id,
            action='chore_completed',
            details={
                'chore_id': chore_id,
                'chore_name': chore_name
            }
        )

    def log_reward_claim(self, user_id, reward_id, reward_name, coins_spent):
        self.log_activity(
            user_id=user_id,
            action='reward_claimed',
            details={
                'reward_id': reward_id,
                'reward_name': reward_name,
                'coins_spent': coins_spent
            }
        )

    def log_goal_achievement(self, family_id, goal_id, goal_name):
        self.log_activity(
            user_id=family_id,  # Using family_id in this case
            action='goal_achieved',
            details={
                'goal_id': goal_id,
                'goal_name': goal_name
            }
        )

    def log_error(self, user_id, error_type, error_details):
        self.log_activity(
            user_id=user_id,
            action='error',
            details={
                'error_type': error_type,
                'error_details': error_details
            },
            level=logging.ERROR
        )
