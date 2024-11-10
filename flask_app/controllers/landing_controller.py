from flask import Blueprint, render_template, request

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    # Get version from query parameter, default to 1
    return render_template(f'landing/landingpage.html')
