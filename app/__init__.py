from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from config.py

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Import and register your blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    from app.billing import billing_bp  # Import billing blueprint with Stripe integration
    from app.admin import admin_bp  # Import admin blueprint
    from app.bulk_certificates import bulk_bp  # Import bulk certificates blueprint
    from app.analytics import analytics_bp  # Import analytics blueprint

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(billing_bp)  # Register billing blueprint
    app.register_blueprint(admin_bp)  # Register admin blueprint
    app.register_blueprint(bulk_bp)  # Register bulk certificates blueprint
    app.register_blueprint(analytics_bp)  # Register analytics blueprint

    # Initialize security features
    from app.security import init_security, handle_errors, generate_error_templates, apply_rate_limits
    limiter = init_security(app)
    handle_errors(app)
    generate_error_templates()

    # Apply rate limits after blueprints are registered
    apply_rate_limits(app, limiter)

    return app
