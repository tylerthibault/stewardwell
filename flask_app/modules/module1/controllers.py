from flask import Blueprint, render_template
from flask_app.modules.module1.models import Module1Model

module1_bp = Blueprint('module1', __name__, url_prefix='/module1',
                      template_folder='templates')

@module1_bp.route('/')
def index():
    items = Module1Model.get_items()
    return render_template('module1_template.html', items=items)
