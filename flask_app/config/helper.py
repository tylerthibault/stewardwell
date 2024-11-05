from functools import wraps
from flask import session, redirect, flash, request
from flask_app.models.users import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            flash("Please log in first!", "danger")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            flash("Please log in first!", "danger")
            return redirect('/login')
        
        # Check if user is a parent
        user = User.get(session_token=session['session_token'])
        if not user or not any(m.role == 'parent' for m in user.family_memberships):
            flash("Parent access required", "danger")
            return redirect('/dashboard')
            
        return f(*args, **kwargs)
    return decorated_function

def kid_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            # Check if we came from pin login or regular login
            referrer = request.referrer or ''
            if 'pin-login' in referrer:
                flash("Please log in first!", "danger")
                return redirect('/pin-login')
            else:
                flash("Please log in first!", "danger")
                return redirect('/login')
        
        # Check if user is a child or parent viewing as child
        if 'viewing_as_child' in session:
            # Parent viewing as child
            return f(*args, **kwargs)
        
        user = User.get(session_token=session['session_token'])
        if not user or not user.is_child:
            # If user is not a child and not viewing as child, redirect to dashboard
            flash("Kid access required", "danger")
            return redirect('/dashboard')
            
        return f(*args, **kwargs)
    return decorated_function
