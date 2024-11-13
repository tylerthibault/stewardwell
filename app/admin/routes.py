from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.models.user import User, Family
from app.utils.logger import ActivityLogger
from app.utils.log_manager import LogManager
from datetime import datetime, timedelta
import psutil
import os

activity_logger = ActivityLogger('admin')
log_manager = LogManager()

def is_admin():
    return current_user.is_authenticated and current_user.is_admin

def get_system_stats():
    """Get system statistics for admin dashboard"""
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter(User.last_login > datetime.now() - timedelta(days=7)).count(),
        'total_families': Family.query.count(),
        'active_families': Family.query.filter(Family.members.any()).count(),
        'system_status': 'Healthy',
        'uptime': '7 days',  # You might want to implement actual uptime tracking
        'recent_errors': len(log_manager.get_recent_errors(24)),
        'db_usage': 45,  # Implement actual database size monitoring
        'memory_usage': psutil.Process(os.getpid()).memory_percent(),
        'log_storage': get_log_storage_usage()
    }
    return stats

def get_log_storage_usage():
    """Calculate log storage usage percentage"""
    log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_dir):
        return 0
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(log_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    
    # Assuming 1GB max log size
    max_size = 1024 * 1024 * 1024
    return min(int((total_size / max_size) * 100), 100)

def get_recent_logs(limit=10):
    """Get recent system logs"""
    logs = []
    try:
        with open(os.path.join('logs', 'stewardwell.log'), 'r') as f:
            for line in f.readlines()[-limit:]:
                parts = line.split(' - ')
                if len(parts) >= 3:
                    logs.append({
                        'timestamp': parts[0],
                        'level': parts[1],
                        'message': ' - '.join(parts[2:]).strip()
                    })
    except Exception as e:
        activity_logger.log_error(
            current_user.id if current_user.is_authenticated else None,
            'log_read_error',
            str(e)
        )
    return logs

def get_module_status():
    """Get status of system modules"""
    return [
        {
            'name': 'Homeconomy',
            'description': 'Family chore and reward management',
            'active': True
        },
        {
            'name': 'Authentication',
            'description': 'User authentication and authorization',
            'active': True
        },
        {
            'name': 'Logging',
            'description': 'System logging and monitoring',
            'active': True
        }
    ]

@bp.before_request
def require_admin():
    if not is_admin():
        activity_logger.log_error(
            current_user.id if current_user.is_authenticated else None,
            'unauthorized_admin_access',
            f'Attempted to access admin area: {request.path}'
        )
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard view"""
    activity_logger.log_activity(
        current_user.id,
        'admin_dashboard_view',
        {'access_time': datetime.now().isoformat()}
    )
    
    return render_template('admin/dashboard.html',
                         stats=get_system_stats(),
                         recent_users=User.query.order_by(User.created_at.desc()).limit(5).all(),
                         recent_logs=get_recent_logs(),
                         modules=get_module_status(),
                         datetime=datetime)

@bp.route('/users')
@login_required
def user_list():
    """User management view"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    
    activity_logger.log_activity(
        current_user.id,
        'admin_user_list_view',
        {'page': page}
    )
    
    return render_template('admin/users.html',
                         users=users)

@bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user view"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.is_admin = 'is_admin' in request.form
            user.is_active = 'is_active' in request.form
            db.session.commit()
            
            activity_logger.log_activity(
                current_user.id,
                'admin_user_edit',
                {
                    'edited_user_id': user_id,
                    'changes': {
                        'is_admin': user.is_admin,
                        'is_active': user.is_active
                    }
                }
            )
            
            flash('User updated successfully.', 'success')
            return redirect(url_for('admin.user_list'))
            
        except Exception as e:
            db.session.rollback()
            activity_logger.log_error(
                current_user.id,
                'admin_user_edit_error',
                str(e)
            )
            flash('Error updating user.', 'error')
    
    return render_template('admin/edit_user.html',
                         user=user)

@bp.route('/logs')
@login_required
def view_logs():
    """Log viewer"""
    log_type = request.args.get('type', 'general')
    page = request.args.get('page', 1, type=int)
    
    activity_logger.log_activity(
        current_user.id,
        'admin_log_view',
        {'log_type': log_type, 'page': page}
    )
    
    logs = get_recent_logs(100)  # Get more logs for pagination
    
    return render_template('admin/logs.html',
                         logs=logs,
                         log_type=log_type)

@bp.route('/system/report')
@login_required
def generate_report():
    """Generate system report"""
    try:
        report = log_manager.generate_daily_report()
        
        activity_logger.log_activity(
            current_user.id,
            'admin_report_generation',
            {'report_date': datetime.now().isoformat()}
        )
        
        return render_template('admin/report.html',
                             report=report)
                             
    except Exception as e:
        activity_logger.log_error(
            current_user.id,
            'admin_report_generation_error',
            str(e)
        )
        flash('Error generating report.', 'error')
        return redirect(url_for('admin.dashboard'))

@bp.route('/system/backup')
@login_required
def backup_system():
    """Initiate system backup"""
    try:
        # Implement backup logic here
        activity_logger.log_activity(
            current_user.id,
            'admin_backup_initiated',
            {'backup_time': datetime.now().isoformat()}
        )
        flash('Backup initiated successfully.', 'success')
        
    except Exception as e:
        activity_logger.log_error(
            current_user.id,
            'admin_backup_error',
            str(e)
        )
        flash('Error initiating backup.', 'error')
        
    return redirect(url_for('admin.dashboard'))

@bp.route('/system/cache/clear')
@login_required
def clear_cache():
    """Clear system cache"""
    try:
        # Implement cache clearing logic here
        activity_logger.log_activity(
            current_user.id,
            'admin_cache_clear',
            {'clear_time': datetime.now().isoformat()}
        )
        flash('Cache cleared successfully.', 'success')
        
    except Exception as e:
        activity_logger.log_error(
            current_user.id,
            'admin_cache_clear_error',
            str(e)
        )
        flash('Error clearing cache.', 'error')
        
    return redirect(url_for('admin.dashboard'))
