from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from app.utils.logger import get_logger

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = get_logger()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superuser:
            logger.warning("Non-admin user attempted to access admin area", 
                         extra={"user_id": current_user.id if current_user.is_authenticated else None})
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    return render_template('admin/users.html')

@admin_bp.route('/families')
@login_required
@admin_required
def families():
    return render_template('admin/families.html') 