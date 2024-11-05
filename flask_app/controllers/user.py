from flask_app import app, db 
from flask import render_template, redirect, request, flash, session
from flask_app.config.helper import login_required, kid_required, parent_required
from flask_app.models import users
from flask_app.models.families import Family
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
import os

# ********* Profile *********
@app.route('/profile')
@login_required
def profile():
    context = {
        'user': users.User.get(session_token=session['session_token'])
    }
    return render_template('/inside/profile.html', **context)

@app.route('/settings')
@login_required
def settings():
    context = {
        'user': users.User.get(session_token=session['session_token'])
    }
    return render_template('/inside/settings.html', **context)

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    user = users.User.get(session_token=session['session_token'])
    if not user:
        flash("User not found", "danger")
        return redirect('/logout')
    
    # Get module settings from form
    settings = {
        'module_chores': 'module_chores' in request.form,
        'module_budget': 'module_budget' in request.form
    }
    
    # Initialize settings if None
    if user.settings is None:
        user.settings = {}
    
    # Update settings
    user.settings.update(settings)
    
    try:
        # Force the settings column to be marked as modified
        flag_modified(user, 'settings')
        db.session.commit()
        
        # Add debug flash message
        flash(f"Settings updated: Chores={'module_chores' in request.form}, Budget={'module_budget' in request.form}", "info")
        flash("Settings updated successfully!", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error updating settings: " + str(e), "danger")
    
    return redirect('/settings')


# ********* LOGIN *********
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Display the login form or process login data."""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Process POST request
    email = request.form['email']
    password = request.form['password']
    
    # Attempt to find user by email
    user = users.User.get_by_email(email)
    if not user or not user.check_password(password):
        flash("Invalid email or password", "error")
        return redirect('/login')
    
    # Set session token for logged-in user
    user.generate_session_token()
    session['session_token'] = user.session_token
    
    flash("Login successful!", "success")
    return redirect('/dashboard')


# ********* LOGOUT *********
@app.route('/logout')
def logout():
    """Log the user out by clearing the session."""
    session.pop('user', None)
    session.pop('session_token', None)
    flash("You have been logged out.", "info")
    return redirect('/')

# ********* CREATE *********
@app.route('/register')
def users_new():
    """Display form to create a new user."""
    return render_template('register.html')

@app.route('/user/create', methods=['POST'])
def users_create():
    """Process form data to create a new user."""
    data = {**request.form}
    
    # Validate form data
    if not users.User.validator(**data):
        return redirect('/register')
    
    # Create user in the database
    user = users.User.create_one(**data)
    if not user:
        return redirect('/register')

    session['session_token'] = user.session_token
    flash("Account created successfully!", "success")
    return redirect('/dashboard')


# ********* READ *********
@app.route('/user')
def users_index():
    """Display a list of all users."""
    context = {
        'all_users': users.User.get_all()
    }
    return render_template('pages/user/users_index.html', **context)

@app.route('/user/<int:id>')
def users_show(id):
    """Display details for a specific user."""
    user = users.User.get(id=id)
    if not user:
        flash("User not found.", "error")
        return redirect('/user')
    
    context = {
        'user': user
    }
    return render_template('pages/user/users_show.html', **context)


# ********* UPDATE *********
@app.route('/user/<int:id>/edit')
def users_edit(id):
    """Display form to edit an existing user."""
    user = users.User.get(id=id)
    if not user:
        flash("User not found.", "error")
        return redirect('/user')
    
    context = {
        'user': user
    }
    return render_template('pages/user/users_edit.html', **context)

@app.route('/user/<int:id>/update', methods=['POST'])
def users_update(id):
    """Process form data to update an existing user."""
    data = {**request.form}
    
    # Validate form data
    if not users.User.validator(**data):
        flash("Invalid user data. Please correct the errors and try again.", "error")
        return redirect(f'/user/{id}/edit')
    
    # Update user in the database
    users.User.update_one({'id': id}, **data)
    flash("User updated successfully!", "success")
    return redirect(f'/user/{id}')


# ********* DELETE *********
@app.route('/user/<int:id>/delete', methods=['POST'])
def users_delete(id):
    """Delete a specific user."""
    if users.User.delete_one(id=id):
        flash("User deleted successfully!", "success")
    else:
        flash("Error deleting user. User may not exist.", "error")
    return redirect('/user')


# ********* PIN LOGIN *********
@app.route('/pin-login', methods=['GET', 'POST'])
def pin_login():
    """Handle kid's PIN-based login"""
    if request.method == 'GET':
        # Get recently logged in children
        recent_children = users.User.get_recent_children()
        return render_template('pin_login.html', recent_children=recent_children)
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    pin = request.form.get('pin')
    
    # Find child by name and PIN
    user = users.User.query.filter_by(
        first_name=first_name,
        last_name=last_name,
        pin_code=pin,
        is_child=True
    ).first()
    
    if not user:
        flash("Sorry, we couldn't find you. Please check your name and PIN.", "danger")
        return redirect('/pin-login')
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    session['session_token'] = user.generate_session_token()
    flash(f"Welcome back, {user.first_name}!", "success")
    return redirect('/kid/dashboard')

@app.route('/join-family')
@login_required
def join_family():
    """Display form to join an existing family"""
    context = {
        'user': users.User.get(session_token=session['session_token'])
    }
    return render_template('inside/join_family.html', **context)

@app.route('/family/<int:family_id>/leave', methods=['POST'])
@login_required
def leave_family(family_id):
    """Handle leaving a family"""
    user = users.User.get(session_token=session['session_token'])
    if not user:
        flash("User not found", "danger")
        return redirect('/logout')
    
    # Check if user is in this family
    membership = next((m for m in user.family_memberships if m.family_id == family_id), None)
    if not membership:
        flash("You are not a member of this family", "danger")
        return redirect('/settings')
    
    # Don't allow the last parent to leave
    if membership.role == 'parent':
        parent_count = sum(1 for m in membership.family.members if m.role == 'parent')
        if parent_count <= 1:
            flash("Cannot leave family: You are the last parent", "danger")
            return redirect('/settings')
    
    try:
        db.session.delete(membership)
        db.session.commit()
        flash("Successfully left the family", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error leaving family: " + str(e), "danger")
    
    return redirect('/settings')

@app.route('/kid/settings')
@kid_required
def kid_settings():
    """Display kid's settings page"""
    if 'viewing_as_child' in session:
        user = users.User.query.get(session['viewing_as_child']['id'])
        family_id = session['viewing_as_child']['family_id']
        family = Family.query.get(family_id)
    else:
        user = users.User.get(session_token=session['session_token'])
        family = user.get_primary_family()
    
    # Get list of avatar files from the directory
    avatar_path = os.path.join(app.static_folder, 'img', 'avatars')
    avatars = []
    if os.path.exists(avatar_path):
        avatars = [f.split('.')[0] for f in os.listdir(avatar_path) 
                  if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    context = {
        'user': user,
        'family': family,  # Add family to context
        'avatars': sorted(avatars)  # Sort alphabetically for consistent display
    }
    return render_template('inside/kid_settings.html', **context)

@app.route('/kid/settings/update', methods=['POST'])
@kid_required
def update_kid_settings():
    """Update kid's settings"""
    if 'viewing_as_child' in session:
        user = users.User.query.get(session['viewing_as_child']['id'])
    else:
        user = users.User.get(session_token=session['session_token'])
    
    if not user:
        flash("User not found", "danger")
        return redirect('/logout')
    
    # Initialize settings if None
    if user.settings is None:
        user.settings = {}
    
    # Update avatar
    if 'avatar' in request.form:
        user.settings['avatar'] = request.form['avatar']
    
    try:
        flag_modified(user, 'settings')
        db.session.commit()
        flash("Settings updated successfully!", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error updating settings: " + str(e), "danger")
    
    return redirect('/kid/settings')

