from flask import Flask, render_template, session, redirect, url_for, flash, request
import os
import json
from datetime import timedelta
import time

# Import blueprints
from blueprints.setAccess.routes import setAccess_bp
from blueprints.api.routes import api_bp
from blueprints.navigation.routes import navigation_bp
from blueprints.navigation_api import navigation_api_bp
from blueprints.page2.routes import bp as page2_bp

# Import services
from services.navigation_service import NavigationService

# Import error handlers
from utils.error_handlers import register_error_handlers, NotFoundError

app = Flask(__name__)

# Security configurations
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Register blueprints
app.register_blueprint(setAccess_bp)
app.register_blueprint(api_bp)
app.register_blueprint(navigation_bp)
app.register_blueprint(navigation_api_bp)
app.register_blueprint(page2_bp)

# Register error handlers
register_error_handlers(app)

# Load navigation data from JSON file with caching
_navigation_cache = None
_navigation_cache_time = None
CACHE_TIMEOUT = 300  # 5 minutes

def load_navigation():
    global _navigation_cache, _navigation_cache_time
    current_time = time.time()
    
    # Return cached data if it's still valid
    if _navigation_cache and _navigation_cache_time and (current_time - _navigation_cache_time) < CACHE_TIMEOUT:
        return _navigation_cache
    
    try:
        # Use the NavigationService to load navigation data
        _navigation_cache = NavigationService.load_navigation()
        _navigation_cache_time = current_time
        return _navigation_cache
    except Exception as e:
        app.logger.error(f"Error loading navigation data: {str(e)}")
        return []

# Context processor to make navigation_data available to all templates
@app.context_processor
def inject_navigation():
    return {'navigation_data': load_navigation()}

@app.route("/")
def index():
    return render_template("base.html")

@app.route("/admin")
def admin():
    if session.get('user_role') != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    return render_template("admin.html")

@app.route("/page<int:num>")
def load_page(num):
    template_name = f"page{num}.html"
    if not os.path.exists(os.path.join(app.template_folder, template_name)):
        raise NotFoundError(f"Page {num} not found")
    return render_template(template_name)

@app.route("/page<int:num>_<int:subnum>")
def load_subpage(num, subnum):
    template_name = f"page{num}_{subnum}.html"
    if not os.path.exists(os.path.join(app.template_folder, template_name)):
        raise NotFoundError(f"Page {num}_{subnum} not found")
    return render_template(template_name)

if __name__ == "__main__":
    app.run(debug=True, port=5800)