from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, Family, generate_family_code
from app import db, bcrypt
from app.forms.auth import RegistrationForm, LoginForm, PinLoginForm
from app.utils.logger import get_logger

auth_bp = Blueprint('auth', __name__)

logger = get_logger()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logger.info("Already authenticated user attempted to access login page", 
                   extra={"user_id": current_user.id})
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            logger.info("User logged in successfully", 
                       extra={"user_id": user.id, "email": user.email})
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            logger.warning("Failed login attempt", 
                         extra={"email": form.email.data, "ip": request.remote_addr})
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/parent-login', methods=['GET', 'POST'])
def parent_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.debug(f"Login attempt for email: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user:
            current_app.logger.debug("No user found with this email")
            flash('No account found with this email.', 'danger')
            return render_template('auth/parent_login.html', form=form)
            
        if not user.is_parent:
            current_app.logger.debug("User is not a parent")
            flash('This account is not registered as a parent account.', 'danger')
            return render_template('auth/parent_login.html', form=form)
            
        if not bcrypt.check_password_hash(user.password_hash, form.password.data):
            current_app.logger.debug("Invalid password")
            flash('Invalid password.', 'danger')
            return render_template('auth/parent_login.html', form=form)
        
        # If we get here, all checks passed
        login_user(user, remember=form.remember.data)
        current_app.logger.debug(f"User {user.username} logged in successfully")
        
        next_page = request.args.get('next')
        return redirect(next_page if next_page else url_for('main.index'))
    
    # If form validation failed, log the errors
    if form.errors:
        current_app.logger.debug(f"Form validation errors: {form.errors}")
    
    return render_template('auth/parent_login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if current_user.is_authenticated:
            logger.info("Authenticated user attempted to access register page", 
                       extra={"user_id": current_user.id})
            return redirect(url_for('main.index'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
            # Create family
            family = Family(
                name=f"{form.username.data}'s Family",
                family_code=generate_family_code()
            )
            db.session.add(family)
            db.session.flush()
            
            # Create user
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password,
                is_parent=True,
                family_id=family.id,
                avatar='fa-user-circle'
            )
            
            db.session.add(user)
            db.session.commit()
            
            logger.info("New user registered successfully", 
                       extra={
                           "username": user.username,
                           "email": user.email,
                           "family_code": family.family_code
                       })
            
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        db.session.rollback()
        logger.error("Error during user registration", 
                    exc_info=True,
                    extra={"form_data": request.form})
        flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/child-login', methods=['GET', 'POST'])
def child_login():
    if request.method == 'POST':
        child_id = request.form.get('child_id')
        pin = request.form.get('pin')
        
        if not all([child_id, pin]):
            flash('Please provide all required information.', 'danger')
            return redirect(url_for('auth.child_login'))
        
        child = User.query.get(child_id)
        if not child or child.is_parent:
            flash('Invalid login attempt.', 'danger')
            return redirect(url_for('auth.child_login'))
        
        if child.pin != pin:
            flash('Incorrect PIN.', 'danger')
            return redirect(url_for('auth.child_login'))
        
        login_user(child)
        return redirect(url_for('main.dashboard'))
    
    # Get family from session
    family_code = session.get('family_code')
    family = None
    if family_code:
        family = Family.query.filter_by(family_code=family_code).first()
    
    return render_template('auth/child_login.html', family=family)

@auth_bp.route('/verify-family-code', methods=['POST'])
def verify_family_code():
    family_code = request.form.get('family_code', '').upper()
    family = Family.query.filter_by(family_code=family_code).first()
    
    if not family:
        flash('Invalid family code.', 'danger')
        return redirect(url_for('auth.child_login'))
    
    # Store family code in session
    session['family_code'] = family_code
    return redirect(url_for('auth.child_login'))

@auth_bp.route('/reset-family-code', methods=['POST'])
def reset_family_code():
    session.pop('family_code', None)
    return '', 204

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 