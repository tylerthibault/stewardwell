from flask_app import app
from flask import render_template, redirect, session
from flask_app.config.helper import login_required
from flask_app.models import users
from flask_app.controllers.family import serialize_member  # Import the serializer

@app.template_filter('serialize_member')
def serialize_member_filter(member):
    """Template filter to serialize FamilyMember objects"""
    return serialize_member(member)

@app.route('/')
def index():
    if 'session_token' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    context = {
        'user': users.User.get(session_token=session['session_token'])
    }
    return render_template('/inside/dashboard.html', **context)
