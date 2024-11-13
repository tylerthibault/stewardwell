from flask import Blueprint

bp = Blueprint('homeconomy', __name__, url_prefix='/homeconomy')

from app.modules.homeconomy import routes
