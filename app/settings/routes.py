from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.settings import bp
from app.settings.forms import ProfileForm, SecurityForm, NotificationForm, AppearanceForm
from app.utils.logger import ActivityLogger
from datetime import datetime

activity_logger = ActivityLogger('settings')

@bp.route('/')
@login_required
def index():
    """Main settings page"""
    settings = current_user.get_settings()
    return render_template('settings/index.html', title='Settings', settings=settings)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile settings"""
    form = ProfileForm()
    settings = current_user.get_settings()
    
    if request.method == 'GET':
        form.email.data = current_user.email
        if current_user.user_type == 'parent' and current_user.family:
            form.family_name.data = current_user.family.name
        form.email_updates.data = settings.email_updates
        form.activity_notifications.data = settings.activity_notifications
    
    if form.validate_on_submit():
        try:
            current_user.email = form.email.data
            if current_user.user_type == 'parent' and current_user.family:
                current_user.family.name = form.family_name.data
            
            # Update email preferences
            settings.update_email_preferences({
                'email_updates': form.email_updates.data,
                'activity_notifications': form.activity_notifications.data
            })
            
            activity_logger.log_activity(
                current_user.id,
                'profile_updated',
                {
                    'email': current_user.email,
                    'email_updates': form.email_updates.data,
                    'activity_notifications': form.activity_notifications.data
                }
            )
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('settings.profile'))
        except Exception as e:
            activity_logger.log_error(
                current_user.id,
                'profile_update_error',
                str(e)
            )
            flash('Error updating profile.', 'error')
            
    return render_template('settings/profile.html', title='Profile Settings', form=form)

@bp.route('/notifications', methods=['GET', 'POST'])
@login_required
def notifications():
    """Notification settings"""
    form = NotificationForm()
    settings = current_user.get_settings()
    
    if request.method == 'GET':
        # Populate form with current settings
        form.email_chores.data = settings.email_chores
        form.email_rewards.data = settings.email_rewards
        form.email_goals.data = settings.email_goals
        form.inapp_chores.data = settings.inapp_chores
        form.inapp_rewards.data = settings.inapp_rewards
        form.inapp_goals.data = settings.inapp_goals
        form.notification_frequency.data = settings.notification_frequency
        if settings.quiet_hours_start:
            form.quiet_hours_start.data = settings.quiet_hours_start
        if settings.quiet_hours_end:
            form.quiet_hours_end.data = settings.quiet_hours_end
    
    if form.validate_on_submit():
        try:
            # Update notification preferences
            settings.update_notifications({
                'email_chores': form.email_chores.data,
                'email_rewards': form.email_rewards.data,
                'email_goals': form.email_goals.data,
                'inapp_chores': form.inapp_chores.data,
                'inapp_rewards': form.inapp_rewards.data,
                'inapp_goals': form.inapp_goals.data,
                'notification_frequency': form.notification_frequency.data,
                'quiet_hours_start': form.quiet_hours_start.data,
                'quiet_hours_end': form.quiet_hours_end.data
            })
            
            activity_logger.log_activity(
                current_user.id,
                'notifications_updated',
                settings.get_notification_settings()
            )
            
            flash('Notification settings updated!', 'success')
            return redirect(url_for('settings.notifications'))
        except Exception as e:
            activity_logger.log_error(
                current_user.id,
                'notifications_update_error',
                str(e)
            )
            flash('Error updating notification settings.', 'error')
            
    return render_template('settings/notifications.html', title='Notification Settings', form=form)

@bp.route('/security', methods=['GET', 'POST'])
@login_required
def security():
    """Security settings"""
    form = SecurityForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('settings/security.html', title='Security Settings', form=form)
            
        try:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            activity_logger.log_activity(
                current_user.id,
                'password_changed',
                {'timestamp': datetime.utcnow().isoformat()}
            )
            
            flash('Password updated successfully!', 'success')
            return redirect(url_for('settings.security'))
        except Exception as e:
            activity_logger.log_error(
                current_user.id,
                'password_change_error',
                str(e)
            )
            flash('Error updating password.', 'error')
            
    return render_template('settings/security.html', title='Security Settings', form=form)

@bp.route('/appearance', methods=['GET', 'POST'])
@login_required
def appearance():
    """Appearance settings"""
    form = AppearanceForm()
    settings = current_user.get_settings()
    
    if request.method == 'GET':
        # Populate form with current settings
        form.theme.data = settings.theme
        form.color_scheme.data = settings.color_scheme
        form.font_size.data = settings.font_size
        form.density.data = settings.density
        form.enable_animations.data = settings.enable_animations
        form.reduce_motion.data = settings.reduce_motion
    
    if form.validate_on_submit():
        try:
            # Update appearance preferences
            settings.update_appearance({
                'theme': form.theme.data,
                'color_scheme': form.color_scheme.data,
                'font_size': form.font_size.data,
                'density': form.density.data,
                'enable_animations': form.enable_animations.data,
                'reduce_motion': form.reduce_motion.data
            })
            
            activity_logger.log_activity(
                current_user.id,
                'appearance_updated',
                settings.get_appearance_settings()
            )
            
            flash('Appearance settings updated!', 'success')
            return redirect(url_for('settings.appearance'))
        except Exception as e:
            activity_logger.log_error(
                current_user.id,
                'appearance_update_error',
                str(e)
            )
            flash('Error updating appearance settings.', 'error')
            
    return render_template('settings/appearance.html', title='Appearance Settings', form=form)

@bp.route('/update-theme', methods=['POST'])
@login_required
def update_theme():
    """Update theme via AJAX"""
    try:
        data = request.get_json()
        theme = data.get('theme')
        if theme in ['light', 'dark', 'system']:
            settings = current_user.get_settings()
            settings.update_appearance({'theme': theme})
            
            activity_logger.log_activity(
                current_user.id,
                'theme_updated',
                {'theme': theme}
            )
            
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Invalid theme'}), 400
    except Exception as e:
        activity_logger.log_error(
            current_user.id,
            'theme_update_error',
            str(e)
        )
        return jsonify({'success': False, 'error': str(e)}), 500
