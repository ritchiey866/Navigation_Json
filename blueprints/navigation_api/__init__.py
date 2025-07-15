from flask import Blueprint

# Create the blueprint
navigation_api_bp = Blueprint('navigation_api', __name__, url_prefix='/api/navigation')

# Import routes
from . import routes 