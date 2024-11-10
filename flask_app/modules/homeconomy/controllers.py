from flask import Blueprint, render_template
from flask_app.modules.homeconomy.models import HomeconomyModel

homeconomy_bp = Blueprint('homeconomy', __name__, url_prefix='/homeconomy',
                         template_folder='templates')

@homeconomy_bp.route('/')
def index():
    items = HomeconomyModel.get_items()
    return render_template('homeconomy_template.html', items=items)
