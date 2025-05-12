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
    # Initialize Flask
    app = Flask(__name__, static_folder="static", template_folder="templates")
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

    # Initialize database: create tables and verify connectivity
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
            'script-src': "'self' 'unsafe-inline' https://code.jquery.com",
            'style-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
            'img-src': "'self' data:",
            'media-src': "'self'",
            'frame-src': "'self' https://www.google.com"
        }
    )

    # Register API blueprint under /api
    from app.core import bp as core_blueprint
    app.register_blueprint(core_blueprint, url_prefix="/api")

    # SPA catch-all: serve index.html for any non-API path
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_ui(path):
        if path.startswith('api/'):
            return app.send_static_file('404.html'), 404
        return render_template('index.html')

    # Register error handlers
    register_error_handlers(app)

    return app
