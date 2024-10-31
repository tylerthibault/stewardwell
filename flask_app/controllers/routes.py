from flask_app import app
from flask import render_template, redirect, session, request
from flask_app.config.helper import login_required
from flask_app.models import users



@app.route('/')
def index():
    if 'session_token' in session:
        return redirect('/dashboard')
    return render_template('/index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    
    context = {
        'user': users.User.get(session_token=session.get('session_token'))
    }
    return render_template('/inside/dashboard.html', **context)
