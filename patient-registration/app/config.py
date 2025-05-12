from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    SECRET_KEY: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USE_TLS: bool
    MAIL_USE_SSL: bool
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    ADMIN_EMAIL: str
    FLASK_LIMITER_STORAGE_URI: str = "memory://"

class ProductionConfig:
    """Base configuration for production environment."""
    def __init__(self):
        self.settings = Settings()

    # Flask configuration attributes
    SECRET_KEY = property(lambda self: self.settings.SECRET_KEY or os.urandom(24))
    SQLALCHEMY_DATABASE_URI = property(lambda self: self.settings.SQLALCHEMY_DATABASE_URI)
    MAIL_SERVER = property(lambda self: self.settings.MAIL_SERVER)
    MAIL_PORT = property(lambda self: self.settings.MAIL_PORT)
    MAIL_USE_TLS = property(lambda self: self.settings.MAIL_USE_TLS)
    MAIL_USE_SSL = property(lambda self: self.settings.MAIL_USE_SSL)
    MAIL_USERNAME = property(lambda self: self.settings.MAIL_USERNAME)
    MAIL_PASSWORD = property(lambda self: self.settings.MAIL_PASSWORD)
    ADMIN_EMAIL = property(lambda self: self.settings.ADMIN_EMAIL)
    FLASK_LIMITER_STORAGE_URI = property(lambda self: self.settings.FLASK_LIMITER_STORAGE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUDIT_LOG_FILE = '/app/logs/audit.log'

    @staticmethod
    def init_app(app):
        settings = Settings()
        app.config.update(
            SECRET_KEY=settings.SECRET_KEY or os.urandom(24),
            SQLALCHEMY_DATABASE_URI=settings.SQLALCHEMY_DATABASE_URI,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_USE_TLS=settings.MAIL_USE_TLS,
            MAIL_USE_SSL=settings.MAIL_USE_SSL,
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            ADMIN_EMAIL=settings.ADMIN_EMAIL,
            FLASK_LIMITER_STORAGE_URI=settings.FLASK_LIMITER_STORAGE_URI,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            AUDIT_LOG_FILE='/app/logs/audit.log'
        )
