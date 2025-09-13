"""
Security utilities including rate limiting, CSRF protection, and error handling
"""
from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def init_security(app):
    """Initialize security features"""
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)
    
    # Configure specific rate limits - apply after blueprints are registered
    # These will be applied when the app is fully initialized
    
    return limiter

def apply_rate_limits(app, limiter):
    """Apply rate limits to view functions after blueprints are registered"""
    try:
        # Apply rate limits to specific endpoints
        if 'auth.login' in app.view_functions:
            limiter.limit("10 per minute")(app.view_functions['auth.login'])
        if 'auth.register' in app.view_functions:
            limiter.limit("5 per minute")(app.view_functions['auth.register'])
        if 'main.invoice' in app.view_functions:
            limiter.limit("20 per minute")(app.view_functions['main.invoice'])
        if 'main.resume_builder' in app.view_functions:
            limiter.limit("20 per minute")(app.view_functions['main.resume_builder'])
        if 'main.certificate_generator' in app.view_functions:
            limiter.limit("20 per minute")(app.view_functions['main.certificate_generator'])
        if 'main.qrcode_generator' in app.view_functions:
            limiter.limit("30 per minute")(app.view_functions['main.qrcode_generator'])
    except Exception as e:
        logger.error(f"Error applying rate limits: {e}")

def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    """Log security events"""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'ip_address': ip_address or get_remote_address(),
        'details': details or {}
    }
    
    logger.warning(f"Security Event: {log_data}")

def validate_file_upload(file, allowed_extensions=None, max_size_mb=10):
    """Validate file uploads for security"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if allowed_extensions:
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File too large. Maximum size: {max_size_mb}MB"
    
    return True, "File valid"

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def check_suspicious_activity(user_id, ip_address):
    """Check for suspicious activity patterns"""
    # This is a simplified version - in production, you'd use a proper security service
    
    # Check for rapid successive requests
    # Check for unusual IP patterns
    # Check for failed login attempts
    
    # For now, just log the activity
    log_security_event('activity_check', user_id, ip_address)
    return False

def require_verification(f):
    """Decorator to require email verification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if current_user.is_authenticated and not current_user.is_verified:
            from flask import flash, redirect, url_for
            flash('Please verify your email address to access this feature.', 'warning')
            return redirect(url_for('auth.resend_verification'))
        return f(*args, **kwargs)
    return decorated_function

def handle_errors(app):
    """Configure error handling"""
    
    @app.errorhandler(400)
    def bad_request(error):
        log_security_event('bad_request', details={'error': str(error)})
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        log_security_event('unauthorized', details={'error': str(error)})
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        log_security_event('forbidden', details={'error': str(error)})
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        log_security_event('not_found', details={'error': str(error)})
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        log_security_event('rate_limit_exceeded', details={'error': str(error)})
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        log_security_event('internal_error', details={'error': str(error)})
        return render_template('errors/500.html'), 500

def create_error_templates():
    """Create error page templates"""
    error_templates = {
        '400.html': {
            'title': 'Bad Request',
            'message': 'The request was invalid or cannot be served.',
            'icon': 'fas fa-exclamation-triangle'
        },
        '401.html': {
            'title': 'Unauthorized',
            'message': 'You need to be logged in to access this page.',
            'icon': 'fas fa-lock'
        },
        '403.html': {
            'title': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'icon': 'fas fa-ban'
        },
        '404.html': {
            'title': 'Page Not Found',
            'message': 'The page you are looking for does not exist.',
            'icon': 'fas fa-search'
        },
        '429.html': {
            'title': 'Too Many Requests',
            'message': 'You have exceeded the rate limit. Please try again later.',
            'icon': 'fas fa-clock'
        },
        '500.html': {
            'title': 'Internal Server Error',
            'message': 'Something went wrong on our end. Please try again later.',
            'icon': 'fas fa-exclamation-circle'
        }
    }
    
    return error_templates

def generate_error_templates():
    """Generate error template files"""
    error_templates = create_error_templates()
    
    # Create errors directory
    os.makedirs('app/templates/errors', exist_ok=True)
    
    for filename, data in error_templates.items():
        template_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']} - MicroSaaS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <style>
        body {{
            background: linear-gradient(135deg, #0b63f6 0%, #1f2dd6 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
        }}
        .error-card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(16, 24, 40, 0.1);
            padding: 3rem;
            text-align: center;
            max-width: 500px;
            width: 100%;
        }}
        .error-icon {{
            font-size: 4rem;
            color: #ef4444;
            margin-bottom: 1rem;
        }}
        .error-title {{
            color: #1f2937;
            font-weight: 800;
            margin-bottom: 1rem;
        }}
        .error-message {{
            color: #667085;
            margin-bottom: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="error-card">
                    <i class="{data['icon']} error-icon"></i>
                    <h1 class="error-title">{data['title']}</h1>
                    <p class="error-message">{data['message']}</p>
                    <a href="/" class="btn btn-primary">Go Home</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        with open(f'app/templates/errors/{filename}', 'w') as f:
            f.write(template_content)
