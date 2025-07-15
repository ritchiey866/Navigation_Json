from flask import jsonify, render_template
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception class for application errors"""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationError(AppError):
    """Exception raised for validation errors"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthenticationError(AppError):
    """Exception raised for authentication errors"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class AuthorizationError(AppError):
    """Exception raised for authorization errors"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=403, payload=payload)

class NotFoundError(AppError):
    """Exception raised for resource not found errors"""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=404, payload=payload)

def register_error_handlers(app):
    """Register error handlers with the Flask application"""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle application errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        logger.error(f"Application error: {error.message}")
        return response
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        logger.warning(f"Page not found: {request.url}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Server error: {error}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle unexpected errors"""
        logger.error(f"Unexpected error: {error}")
        return render_template('errors/500.html'), 500 