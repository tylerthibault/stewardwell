import uuid
from flask import request, g
import logging

logger = logging.getLogger('flask_app')

class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request_id = str(uuid.uuid4())
        environ['HTTP_X_REQUEST_ID'] = request_id
        return self.app(environ, start_response)

def log_request_info():
    g.request_id = request.environ.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
    logger.info(
        f"Request started",
        extra={
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr
        }
    )
