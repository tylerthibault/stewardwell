from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import User
from app import db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superuser:
            flash('You need to be a superuser to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users')
@login_required
@superuser_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-superuser', methods=['POST'])
@login_required
@superuser_required
def toggle_superuser(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot modify your own superuser status.', 'danger')
    else:
        user.is_superuser = not user.is_superuser
        db.session.commit()
        flash(f'Superuser status for {user.username} has been {"enabled" if user.is_superuser else "disabled"}.', 'success')
    return redirect(url_for('admin.manage_users')) 