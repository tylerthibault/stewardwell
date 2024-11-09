from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_app.models.user import User, Family
from flask_app import db
from flask_app.seed import seed_database
import secrets

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    print("Index route accessed!")
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    family = current_user.family
    if not family:
        flash('You need to be part of a family to access the dashboard.', 'warning')
        return redirect(url_for('main.index'))
        
    family_count = len(family.members)
    family_points = sum(member.family_points for member in family.members)
    family_members = family.members
    recent_activities = []  # TODO: Implement activity tracking
    
    return render_template('main/dashboard.html',
                         family_count=family_count,
                         family_points=family_points,
                         family_members=family_members,
                         recent_activities=recent_activities)
    
    return render_template('main/dashboard.html')

@main_bp.route('/reset-db', methods=['GET', 'POST'])
def reset_db():
    # Only allow in development mode
    if not current_app.debug:
        return "Not available in production.", 403
    
    if request.method == 'GET':
        return render_template('main/reset_db.html')
    
    try:
        # Drop all tables
        db.drop_all()
        # Recreate all tables
        db.create_all()
        flash('Database has been reset successfully!', 'success')
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'danger')
    
    return redirect(url_for('main.index'))

@main_bp.route('/seed-db')
def seed_db():
    # Only allow in development mode
    if not current_app.debug:
        return "Not available in production.", 403
    
    try:
        # Drop existing data
        db.drop_all()
        db.create_all()
        
        # Seed the database
        seed_database()
        flash('Database has been seeded successfully!', 'success')
    except Exception as e:
        flash(f'Error seeding database: {str(e)}', 'danger')
    
    return redirect(url_for('main.index'))
