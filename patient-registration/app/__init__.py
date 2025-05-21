from flask import Flask, render_template, jsonify
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
import structlog
import os
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

from app.config import ProductionConfig
from app.error_handlers import register_error_handlers
from app.extensions import db, limiter, mail
from app.core.models import Patient

migrate = Migrate()

def create_app(config_class=ProductionConfig):
    app = Flask(
        __name__,
        static_folder="static",        # Static files are in app/static/
        static_url_path="/static",     # Serve them at /static
        template_folder="templates"    # Templates are in app/templates/
    )

    app.config.from_object(config_class)
    config_class.init_app(app)

    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL')

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.WriteLoggerFactory(
            open(app.config['AUDIT_LOG_FILE'], 'a')
        )
    )

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    CORS(app)
    limiter.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            db.session.execute(text("SELECT 1"))
            db.session.commit()
            app.logger.info("Database initialized and verified")
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", e)
            raise

    from app.core import bp as core_blueprint
    app.register_blueprint(core_blueprint, url_prefix="/api")

    @app.route('/health')
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "healthy", "database": "connected"}), 200
        except Exception as e:
            app.logger.error("Health check failed", error=str(e))
            return jsonify({"status": "unhealthy", "error": str(e)}), 500

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_ui(path):
        if path.startswith('api/'):
            return app.send_static_file('404.html'), 404
        return render_template('index.html')

    @app.route('/patient-register')
    def patient_register():
        return render_template('index.html')

    register_error_handlers(app)

    try:
        with app.app_context():
            _ = mail.connection
        app.logger.info("Mail extension initialized")
    except Exception as me:
        app.logger.error("Mail failed to initialize: %s", me)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003, debug=True)
