from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from flask_app import db, logger
from flask_app.models.user import User
from flask_app.forms.auth_forms import RegistrationForm

# Remove the url_prefix to make routes more accessible
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('landing.index'))
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Create new user
                user = User(
                    username=form.username.data,
                    email=form.email.data
                )
                user.set_password(form.password.data)
                
                # Add and commit to database
                db.session.add(user)
                db.session.commit()
                
                # Log successful registration
                logger.info(
                    "User registered successfully",
                    extra={
                        'username': user.username,
                        'email': user.email
                    }
                )
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                # Roll back transaction on error
                db.session.rollback()
                
                # Log the error
                logger.error(
                    "Registration failed",
                    extra={
                        'error': str(e),
                        'username': form.username.data,
                        'email': form.email.data
                    }
                )
                flash('An error occurred during registration. Please try again.', 'danger')
        else:
            # Log form validation errors
            logger.warning(
                "Registration form validation failed",
                extra={
                    'errors': form.errors
                }
            )
            # Flash specific validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    # Render registration template with form
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('landing.index'))
    # TODO: Implement login functionality
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing.index'))
