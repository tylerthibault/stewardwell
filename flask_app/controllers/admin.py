from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from flask_app.utils.decorators import superuser_required
from flask_app.models.user import User, Family
from flask_app.models.chore import Chore
from flask_app.utils.logger import get_logger

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = get_logger()

@admin_bp.route('/')
@login_required
@superuser_required
def index():
    try:
        stats = {
            'total_users': User.query.count(),
            'total_families': Family.query.count(),
            'total_chores': Chore.query.count(),
            'total_rewards': 0  # Add this when rewards model is implemented
        }
        return render_template('admin/index.html', stats=stats)
    except Exception as e:
        logger.error("Error loading admin dashboard",
                    exc_info=True,
                    extra={"user_id": current_user.id})
        flash('Error loading admin dashboard.', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/users')
@login_required
@superuser_required
def users():
    return render_template('admin/users.html')

@admin_bp.route('/families')
@login_required
@superuser_required
def families():
    return render_template('admin/families.html')

@admin_bp.route('/system')
@login_required
@superuser_required
def system():
    return render_template('admin/system.html')
  