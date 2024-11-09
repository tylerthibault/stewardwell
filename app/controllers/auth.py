from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, Family
from app import db, bcrypt
from app.forms.auth import RegistrationForm, LoginForm, PinLoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')

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
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            current_app.logger.info(f"Starting registration for user: {form.username.data}")
            
            # Create password hash
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
            # Create user instance
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password,
                is_parent=form.is_parent.data
            )
            current_app.logger.info(f"Created user object: {user.username}, Parent: {user.is_parent}")
            
            # Create family if user is parent
            if form.is_parent.data and form.family_name.data:
                current_app.logger.info(f"Creating family: {form.family_name.data}")
                family = Family(name=form.family_name.data)
                db.session.add(family)
                db.session.flush()
                user.family_id = family.id
                current_app.logger.info(f"Family created with ID: {family.id}")
            
            # Add user to database
            db.session.add(user)
            current_app.logger.info("Added user to session")
            
            # Commit changes
            db.session.commit()
            current_app.logger.info(f"Successfully committed user {user.username} to database")
            
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.parent_login' if user.is_parent else 'auth.child_login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('auth/register.html', form=form)
    
    # If form validation failed, log the errors
    if form.errors:
        current_app.logger.debug(f"Form validation errors: {form.errors}")
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/child-login', methods=['GET', 'POST'])
def child_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = PinLoginForm()
    if form.validate_on_submit():
        # First find the family
        family = Family.query.filter_by(family_code=form.family_code.data.upper()).first()
        
        if not family:
            flash('Invalid family code. Please check with your parents.', 'danger')
            return render_template('auth/child_login.html', form=form)
        
        # Find child by PIN within this family
        child = User.query.filter_by(
            family_id=family.id,
            pin=form.pin.data,
            is_parent=False
        ).first()
        
        if child:
            login_user(child)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid PIN for this family.', 'danger')
    
    return render_template('auth/child_login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 