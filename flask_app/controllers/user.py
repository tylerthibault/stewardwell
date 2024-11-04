from flask_app import app
from flask import render_template, redirect, request, flash, session
from flask_app.config.helper import login_required
from flask_app.models import users

# ********* Profile *********
@app.route('/profile')
@login_required
def profile():
    context = {
        'user': users.User.get(session_token=session['session_token'])
    }
    return render_template('/inside/profile.html', **context)

@app.route('/settings')
def settings():
    context = {
            'user': users.User.get(session_token=session['session_token'])
        }
    return render_template('/inside/settings.html', **context)


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
        return render_template('pin_login.html')
    
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
    
    session['session_token'] = user.generate_session_token()
    flash(f"Welcome back, {user.first_name}!", "success")
    return redirect('/kid/dashboard')

