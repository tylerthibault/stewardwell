from functools import wraps
from flask import session, redirect, url_for, flash
from flask_app.models import users

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if session_token is in the session
        session_token = session.get('session_token')
        if not session_token:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('index'))
        
        # Retrieve user by session_token to confirm they are logged in
        user = users.User.get(session_token=session_token)
        if not user:
            # Clear any invalid session data and redirect to login
            session.pop('session_token', None)
            flash("Your session has expired. Please log in again.", "warning")
            return redirect(url_for('index'))
        
        # If user is valid, proceed with the original function
        return f(*args, **kwargs)
    
    return decorated_function
