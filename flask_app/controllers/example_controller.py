from flask import Blueprint, render_template
from flask_app.models.example_model import ExampleModel

example_bp = Blueprint('example', __name__)

@example_bp.route('/')
def index():
    posts = ExampleModel.get_all()
    return render_template('example_template.html', posts=posts)
