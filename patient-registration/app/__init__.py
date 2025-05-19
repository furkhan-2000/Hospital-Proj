# app/__init__.py

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template
from flask_mail import Mail
from flask_cors import CORS
from flask_talisman import Talisman
from flask_migrate import Migrate
import structlog
import os
from sqlalchemy import text

from app.config import ProductionConfig
from app.error_handlers import register_error_handlers
from app.extensions import db, limiter, mail
from app.core.models import Patient  # Ensure Patient model is registered

# Initialize migrate
migrate = Migrate()

def create_app(config_class=ProductionConfig):
    # Initialize Flask, serve static at root
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="",        # serve /style.css → app/static/style.css
        template_folder="templates"
    )

    # Load the correct config class
    app.config.from_object(config_class)
    config_class.init_app(app)

    # Structured logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.WriteLoggerFactory(
            open(app.config['AUDIT_LOG_FILE'], 'a')
        )
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    CORS(app)
    limiter.init_app(app)

    # Initialize database
    with app.app_context():
        try:
            db.create_all()
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            app.logger.info("Database initialized and verified")
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", e)
            raise

    # Security headers
    Talisman(
        app,
        force_https=False,
        strict_transport_security=False,
        session_cookie_secure=False,
        content_security_policy={
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline' https://code.jquery.com https://unpkg.com",
            'style-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://unpkg.com",
            'img-src': "'self' data:",
            'media-src': "'self'",
            'frame-src': "'self' https://www.google.com",
            'font-src': "'self' data: https://cdnjs.cloudflare.com https://fonts.gstatic.com"
        }
    )

    # Register blueprint
    from app.core import bp as core_blueprint
    app.register_blueprint(core_blueprint, url_prefix="/api")

    # SPA catch-all
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_ui(path):
        if path.startswith('api/'):
            return app.send_static_file('404.html'), 404
        return render_template('index.html')

    # Register error handlers
    register_error_handlers(app)

    # Log mail initialization errors
    try:
        with app.app_context():
            _ = mail.connection
        app.logger.info("Mail extension initialized")
    except Exception as me:
        app.logger.error("Mail failed to initialize: %s", me)

    return app
