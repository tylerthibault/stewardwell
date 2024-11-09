from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask_app.models.user import User, Family, FamilyJoinRequest
from flask_app import db, bcrypt
from flask_app.utils.logger import get_logger
from functools import wraps
from datetime import datetime

family_bp = Blueprint('family', __name__, url_prefix='/family')
logger = get_logger()

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_parent:
            flash('You need to be a parent to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@family_bp.route('/members')
@login_required
@parent_required
def members():
    if not current_user.family:
        flash('You need to be part of a family to view members.', 'warning')
        return redirect(url_for('main.dashboard'))
    
    try:
        family = current_user.family
        parents = User.query.filter_by(family_id=family.id, is_parent=True).all()
        children = User.query.filter_by(family_id=family.id, is_parent=False).all()
        
        # Get pending join requests
        pending_requests = FamilyJoinRequest.query.filter_by(
            family_id=family.id,
            status='pending'
        ).order_by(FamilyJoinRequest.created_at.desc()).all()
        
        return render_template('family/members.html',
                             family=family,
                             parents=parents,
                             children=children,
                             pending_requests=pending_requests)
                             
    except Exception as e:
        logger.error("Error loading family members page",
                    exc_info=True,
                    extra={"user_id": current_user.id})
        flash('Error loading family members.', 'danger')
        return redirect(url_for('main.dashboard'))

@family_bp.route('/add-parent', methods=['POST'])
@login_required
@parent_required
def add_parent():
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')
    
    if not all([email, password, username]):
        flash('Please provide all required fields.', 'danger')
        return redirect(url_for('family.members'))
    
    try:
        # Create new parent user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        parent = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            is_parent=True,
            family_id=current_user.family.id
        )
        
        db.session.add(parent)
        db.session.commit()
        flash(f'Parent account for {username} created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error creating parent account. Email or username might be taken.', 'danger')
    
    return redirect(url_for('family.members'))

@family_bp.route('/add-child', methods=['POST'])
@login_required
@parent_required
def add_child():
    username = request.form.get('username')
    pin = request.form.get('pin')
    
    if not username or not pin:
        flash('Please provide both username and PIN.', 'danger')
        return redirect(url_for('family.members'))
    
    if len(pin) != 4 or not pin.isdigit():
        flash('PIN must be exactly 4 digits.', 'danger')
        return redirect(url_for('family.members'))
    
    # Check if PIN is already used within the same family
    existing_child = User.query.filter_by(
        family_id=current_user.family.id,
        pin=pin,
        is_parent=False
    ).first()
    
    if existing_child:
        flash('This PIN is already used by another child in your family.', 'danger')
        return redirect(url_for('family.members'))
    
    try:
        child = User(
            username=username,
            email=f"{username}@child.local",
            password_hash=bcrypt.generate_password_hash("child-account").decode('utf-8'),
            pin=pin,
            is_parent=False,
            family_id=current_user.family.id,
            parent_id=current_user.id
        )
        
        db.session.add(child)
        db.session.commit()
        flash(f'Child account for {username} created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error creating child account. Username might be taken.', 'danger')
    
    return redirect(url_for('family.members'))

@family_bp.route('/remove-member/<int:member_id>', methods=['POST'])
@login_required
@parent_required
def remove_member(member_id):
    member = User.query.get_or_404(member_id)
    
    if member.family_id != current_user.family.id:
        flash('You can only remove members from your own family.', 'danger')
        return redirect(url_for('family.members'))
    
    if member == current_user:
        flash('You cannot remove yourself from the family.', 'danger')
        return redirect(url_for('family.members'))
    
    try:
        db.session.delete(member)
        db.session.commit()
        flash(f'{member.username} has been removed from the family.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error removing member from family.', 'danger')
    
    return redirect(url_for('family.members'))

@family_bp.route('/edit-child/<int:child_id>', methods=['POST'])
@login_required
@parent_required
def edit_child(child_id):
    child = User.query.get_or_404(child_id)
    
    # Ensure the child belongs to the current user's family
    if child.family_id != current_user.family.id:
        flash('You can only edit children in your own family.', 'danger')
        return redirect(url_for('family.members'))
    
    # Ensure the user being edited is actually a child
    if child.is_parent:
        flash('You can only edit child accounts.', 'danger')
        return redirect(url_for('family.members'))
    
    username = request.form.get('username')
    pin = request.form.get('pin')
    coins = request.form.get('coins')
    
    if not all([username, pin, coins]):
        flash('Please provide all required fields.', 'danger')
        return redirect(url_for('family.members'))
    
    if len(pin) != 4 or not pin.isdigit():
        flash('PIN must be exactly 4 digits.', 'danger')
        return redirect(url_for('family.members'))
    
    try:
        # Check if PIN is already used by another child in the family
        existing_child = User.query.filter(
            User.family_id == current_user.family.id,
            User.pin == pin,
            User.id != child_id,
            User.is_parent == False
        ).first()
        
        if existing_child:
            flash('This PIN is already used by another child in your family.', 'danger')
            return redirect(url_for('family.members'))
        
        child.username = username
        child.pin = pin
        child.coins = int(coins)
        
        db.session.commit()
        flash(f'Child account for {username} updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating child account. Username might be taken.', 'danger')
    
    return redirect(url_for('family.members'))

@family_bp.route('/approve-request/<int:request_id>', methods=['POST'])
@login_required
@parent_required
def approve_request(request_id):
    join_request = FamilyJoinRequest.query.get_or_404(request_id)
    
    # Verify the request is for the current user's family
    if join_request.family_id != current_user.family_id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('family.members'))
    
    try:
        # Update user's family
        join_request.user.family_id = current_user.family_id
        join_request.status = 'accepted'
        join_request.resolved_at = datetime.utcnow()
        
        db.session.commit()
        flash(f'{join_request.user.username} has been added to your family!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error processing request.', 'danger')
        
    return redirect(url_for('family.members'))

@family_bp.route('/reject-request/<int:request_id>', methods=['POST'])
@login_required
@parent_required
def reject_request(request_id):
    join_request = FamilyJoinRequest.query.get_or_404(request_id)
    
    # Verify the request is for the current user's family
    if join_request.family_id != current_user.family_id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('family.members'))
    
    try:
        join_request.status = 'rejected'
        join_request.resolved_at = datetime.utcnow()
        db.session.commit()
        flash('Join request has been rejected.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error processing request.', 'danger')
        
    return redirect(url_for('family.members')) 