from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template
from flask_mail import Mail
from flask_cors import CORS
from flask_talisman import Talisman
import structlog
import os
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.config import ProductionConfig
from app.error_handlers import register_error_handlers
from app.extensions import db, limiter, mail


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
    mail.init_app(app)
    CORS(app)
    limiter.init_app(app)

    # Security headers
    Talisman(
        app,
        force_https=False,
        strict_transport_security=False,
        session_cookie_secure=False,
        content_security_policy={
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline'",
            'style-src': "'self' 'unsafe-inline'",
            'img-src': "'self' data:"
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
            # Let API return its own 404/405
            return app.send_static_file('404.html'), 404
        return render_template('index.html')

    # Ensure database tables exist (and enable WAL)
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("DB tables created or verified successfully")
        except OperationalError as e:
            msg = str(e)
            if "already exists" in msg:
                app.logger.warning("Some tables already exist, skipping creation: %s", msg)
            else:
                app.logger.error("Database initialization failed: %s", msg)
                raise
        try:
            db.session.execute(text("PRAGMA journal_mode=WAL"))
        except Exception as e:
            app.logger.error("Failed to enable WAL mode: %s", e)

    # Register error handlers
    register_error_handlers(app)

    return app
