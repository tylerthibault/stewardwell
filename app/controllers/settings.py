from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db, bcrypt
from app.forms.settings import UpdateProfileForm, ChangePasswordForm
from app.models.user import User, Family, FamilyJoinRequest, ModuleSettings
from app.models.chore import Chore
from datetime import datetime
from functools import wraps
from app.utils.logger import get_logger

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

logger = get_logger()

def parent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_parent:
            flash('You need to be a parent to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = UpdateProfileForm()
    password_form = ChangePasswordForm()
    
    try:
        # Get current module settings
        module_settings = {}
        if current_user.family:
            settings = ModuleSettings.query.filter_by(family_id=current_user.family_id).all()
            module_settings = {
                setting.module_name: setting.is_enabled 
                for setting in settings
            }
        
        if profile_form.submit_profile.data and profile_form.validate():
            current_user.username = profile_form.username.data
            current_user.email = profile_form.email.data
            
            try:
                db.session.commit()
                logger.info("User profile updated successfully",
                           extra={
                               "user_id": current_user.id,
                               "new_username": profile_form.username.data,
                               "new_email": profile_form.email.data
                           })
                flash('Your profile has been updated!', 'success')
            except Exception as e:
                db.session.rollback()
                logger.error("Error updating user profile",
                           exc_info=True,
                           extra={"user_id": current_user.id})
                flash('Error updating profile. Username or email might be taken.', 'danger')
            
            return redirect(url_for('settings.profile'))
            
        elif password_form.submit_password.data and password_form.validate():
            if bcrypt.check_password_hash(current_user.password_hash, password_form.current_password.data):
                current_user.password_hash = bcrypt.generate_password_hash(
                    password_form.new_password.data
                ).decode('utf-8')
                
                try:
                    db.session.commit()
                    logger.info("User password changed successfully",
                              extra={"user_id": current_user.id})
                    flash('Your password has been updated!', 'success')
                except Exception as e:
                    db.session.rollback()
                    logger.error("Error updating user password",
                               exc_info=True,
                               extra={"user_id": current_user.id})
                    flash('Error updating password.', 'danger')
            else:
                logger.warning("Failed password change attempt - incorrect current password",
                             extra={"user_id": current_user.id})
                flash('Current password is incorrect.', 'danger')
                
            return redirect(url_for('settings.profile'))
            
    except Exception as e:
        logger.error("Unexpected error in profile settings",
                    exc_info=True,
                    extra={"user_id": current_user.id})
        flash('An unexpected error occurred.', 'danger')
    
    # Pre-fill profile form with current data
    if request.method == 'GET':
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
    
    return render_template('settings/profile.html', 
                         profile_form=profile_form,
                         password_form=password_form,
                         module_settings=module_settings)

@settings_bp.route('/join-family', methods=['GET', 'POST'])
@login_required
def join_family():
    if request.method == 'POST':
        family_code = request.form.get('family_code')
        if not family_code:
            flash('Please provide a family code.', 'danger')
            return redirect(url_for('settings.pending_requests'))
        
        family = Family.query.filter_by(family_code=family_code.upper()).first()
        if not family:
            flash('Invalid family code. Please check and try again.', 'danger')
            return redirect(url_for('settings.pending_requests'))
        
        # If user is already in this family, no need to request
        if current_user.family_id == family.id:
            flash('You are already a member of this family.', 'info')
            return redirect(url_for('settings.pending_requests'))
        
        try:
            # If user is in another family, remove them
            if current_user.family:
                old_family = current_user.family
                current_user.family_id = None
                flash(f'You have been removed from {old_family.name}.', 'info')
                
                # Cancel any pending requests from the old family
                FamilyJoinRequest.query.filter_by(
                    user_id=current_user.id,
                    status='pending'
                ).delete()
            
            # Create new join request
            join_request = FamilyJoinRequest(
                user_id=current_user.id,
                family_id=family.id
            )
            
            db.session.add(join_request)
            db.session.commit()
            flash(f'Your request to join {family.name} has been sent!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Error processing your request.', 'danger')
        
        return redirect(url_for('settings.pending_requests'))
    
    return render_template('settings/join_family.html')

@settings_bp.route('/pending-requests')
@login_required
def pending_requests():
    # Get incoming requests if user is a parent
    incoming_requests = []
    if current_user.is_parent and current_user.family:
        incoming_requests = FamilyJoinRequest.query.filter_by(
            family_id=current_user.family.id,
            status='pending'
        ).all()
    
    # Get outgoing requests for the current user
    outgoing_requests = FamilyJoinRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(FamilyJoinRequest.created_at.desc()).all()
    
    return render_template('settings/pending_requests.html', 
                         requests=incoming_requests,
                         outgoing_requests=outgoing_requests)

@settings_bp.route('/handle-request/<int:request_id>/<string:action>')
@login_required
def handle_request(request_id, action):
    join_request = FamilyJoinRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the current user's family
    if join_request.family_id != current_user.family.id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('settings.pending_requests'))
    
    if action == 'accept':
        # Add user to family
        user = join_request.user
        user.family_id = current_user.family.id
        join_request.status = 'accepted'
        join_request.resolved_at = datetime.utcnow()
        flash(f'{user.username} has been added to your family!', 'success')
    
    elif action == 'reject':
        join_request.status = 'rejected'
        join_request.resolved_at = datetime.utcnow()
        flash('Request has been rejected.', 'info')
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error processing request.', 'danger')
    
    return redirect(url_for('settings.pending_requests'))

@settings_bp.route('/cancel-request/<int:request_id>', methods=['POST'])
@login_required
def cancel_request(request_id):
    join_request = FamilyJoinRequest.query.get_or_404(request_id)
    
    # Ensure the request belongs to the current user
    if join_request.user_id != current_user.id:
        flash('Invalid request.', 'danger')
        return redirect(url_for('settings.pending_requests'))
    
    # Only allow cancellation of pending requests
    if join_request.status != 'pending':
        flash('This request can no longer be cancelled.', 'warning')
        return redirect(url_for('settings.pending_requests'))
    
    try:
        db.session.delete(join_request)
        db.session.commit()
        flash('Join request cancelled.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error cancelling request.', 'danger')
    
    return redirect(url_for('settings.pending_requests'))

@settings_bp.route('/modules', methods=['GET', 'POST'])
@login_required
@parent_required
def manage_modules():
    # Define available modules
    default_modules = {
        'economy': {
            'name': 'Economy Module',
            'description': 'Chores, Rewards, and Family Goals system',
            'icon': 'fa-coins'
        }
    }
    
    # Add admin module if user is superuser
    if current_user.is_superuser:
        default_modules['admin'] = {
            'name': 'Admin Module',
            'description': 'System administration and management',
            'icon': 'fa-shield-alt'
        }

    if request.method == 'POST':
        try:
            module_name = request.form.get('module_name')
            is_enabled = request.form.get('is_enabled') == 'true'
            
            # Check if setting exists
            setting = ModuleSettings.query.filter_by(
                family_id=current_user.family_id,
                module_name=module_name
            ).first()
            
            if setting:
                setting.is_enabled = is_enabled
            else:
                setting = ModuleSettings(
                    module_name=module_name,
                    is_enabled=is_enabled,
                    family_id=current_user.family_id
                )
                db.session.add(setting)
            
            db.session.commit()
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # Get current settings
    current_settings = {
        setting.module_name: setting.is_enabled 
        for setting in ModuleSettings.query.filter_by(family_id=current_user.family_id).all()
    }
    
    # Merge with defaults
    modules = {
        name: {
            **info,
            'is_enabled': current_settings.get(name, True)
        }
        for name, info in default_modules.items()
    }
    
    return render_template('settings/modules.html', modules=modules)

@settings_bp.route('/child-profile')
@login_required
def child_profile():
    if current_user.is_parent:
        return redirect(url_for('settings.profile'))
    
    # Available avatars
    avatars = [
        {'id': 'ninja', 'icon': 'fa-user-ninja'},
        {'id': 'astronaut', 'icon': 'fa-user-astronaut'},
        {'id': 'superhero', 'icon': 'fa-user-superhero'},
        {'id': 'robot', 'icon': 'fa-robot'},
        {'id': 'alien', 'icon': 'fa-user-alien'},
        {'id': 'graduate', 'icon': 'fa-user-graduate'},
        {'id': 'secret', 'icon': 'fa-user-secret'},
        {'id': 'tie', 'icon': 'fa-user-tie'}
    ]
    
    # Get completed chores count
    completed_chores_count = Chore.query.filter_by(
        assigned_to_id=current_user.id,
        status='completed'
    ).count()
    
    return render_template('settings/child_profile.html',
                         avatars=avatars,
                         completed_chores_count=completed_chores_count)

@settings_bp.route('/update-avatar', methods=['POST'])
@login_required
def update_avatar():
    if current_user.is_parent:
        return redirect(url_for('settings.profile'))
    
    avatar = request.form.get('avatar')
    if avatar:
        try:
            current_user.avatar = avatar
            db.session.commit()
            flash('Avatar updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating avatar.', 'danger')
    
    return redirect(url_for('settings.child_profile'))

@settings_bp.route('/update-pin', methods=['POST'])
@login_required
def update_pin():
    if current_user.is_parent:
        return redirect(url_for('settings.profile'))
    
    current_pin = request.form.get('current_pin')
    new_pin = request.form.get('new_pin')
    confirm_pin = request.form.get('confirm_pin')
    
    if not all([current_pin, new_pin, confirm_pin]):
        flash('Please fill in all PIN fields.', 'danger')
        return redirect(url_for('settings.child_profile'))
    
    if current_pin != current_user.pin:
        flash('Current PIN is incorrect.', 'danger')
        return redirect(url_for('settings.child_profile'))
    
    if new_pin != confirm_pin:
        flash('New PINs do not match.', 'danger')
        return redirect(url_for('settings.child_profile'))
    
    if not new_pin.isdigit() or len(new_pin) != 4:
        flash('PIN must be exactly 4 digits.', 'danger')
        return redirect(url_for('settings.child_profile'))
    
    try:
        current_user.pin = new_pin
        db.session.commit()
        flash('PIN updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating PIN.', 'danger')
    
    return redirect(url_for('settings.child_profile'))