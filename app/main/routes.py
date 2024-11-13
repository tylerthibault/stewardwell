from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        if current_user.user_type == 'parent':
            if not current_user.family:
                return redirect(url_for('homeconomy.create_family'))
            return redirect(url_for('homeconomy.parent_dashboard'))
        else:
            return redirect(url_for('homeconomy.child_dashboard'))
    return render_template('main/index.html', title='Welcome to StewardWell')

@bp.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('main/profile.html', title='Profile')
