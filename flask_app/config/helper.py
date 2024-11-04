from functools import wraps
from flask import session, redirect, flash
from flask_app.models.users import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            flash("Please log in first!", "danger")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def kid_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            flash("Please log in first!", "danger")
            return redirect('/')
        
        user = User.get(session_token=session['session_token'])
        if not user or (not user.is_child and not session.get('viewing_as_child')):
            flash("Access denied", "danger")
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            flash("Please log in first!", "danger")
            return redirect('/')
        
        user = User.get(session_token=session['session_token'])
        if not user or user.is_child:
            flash("Access denied", "danger")
            return redirect('/kid/dashboard')
        return f(*args, **kwargs)
    return decorated_function
