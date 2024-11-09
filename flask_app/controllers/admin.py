from flask import Blueprint, render_template
from flask_login import login_required
from flask_app.utils.decorators import admin_required
from flask_app.models.user import User
from flask_app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    # Get all users from the database
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/families')
@login_required
@admin_required
def families():
    return render_template('admin/families.html')

@admin_bp.route('/system')
@login_required
@admin_required
def system():
    return render_template('admin/system.html')
  