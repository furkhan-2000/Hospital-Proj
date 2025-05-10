import os
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    # Core mail settings
    MAIL_SERVER: str = Field(..., env="MAIL_SERVER")
    MAIL_PORT: int = Field(..., env="MAIL_PORT")
    MAIL_USE_TLS: bool = Field(..., env="MAIL_USE_TLS")
    MAIL_USE_SSL: bool = Field(..., env="MAIL_USE_SSL")
    MAIL_USERNAME: str = Field(..., env="MAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="MAIL_PASSWORD")

    # Admin email for notifications
    ADMIN_EMAIL: str = Field(..., env="ADMIN_EMAIL")

    # Other app-specific settings
    DATABASE_URL: str = Field(default="sqlite:////app/data/app.db", env="DATABASE_URL")
    AUDIT_LOG_FILE: str = Field(default="/app/logs/audit.log", env="AUDIT_LOG_FILE")
    PATIENT_DATA_DIR: str = Field(default="/app/data/patient_data", env="PATIENT_DATA_DIR")

    class SettingsConfigDict:
        # Automatically load .env from project root
        env_file = ".env"
        env_file_encoding = "utf-8"

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "hard-to-guess-string")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = 5003
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    AUDIT_LOG_FILE = os.environ.get("AUDIT_LOG_FILE", "/app/logs/audit.log")
    PATIENT_DATA_DIR = os.environ.get("PATIENT_DATA_DIR", "/app/data/patient_data")

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", Config.__dict__.get("DATABASE_URL")
    )

    @classmethod
    def init_app(cls, app):
        # Load environment via Pydantic and update app.config
        settings = Settings()

        # Update Flask app config from Pydantic settings
        app.config.update(
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_USE_TLS=settings.MAIL_USE_TLS,
            MAIL_USE_SSL=settings.MAIL_USE_SSL,
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            ADMIN_EMAIL=settings.ADMIN_EMAIL,
            SQLALCHEMY_DATABASE_URI=settings.DATABASE_URL,
            AUDIT_LOG_FILE=settings.AUDIT_LOG_FILE,
            PATIENT_DATA_DIR=settings.PATIENT_DATA_DIR
        )

        # Ensure directories exist
        Path(settings.PATIENT_DATA_DIR).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(settings.AUDIT_LOG_FILE)).mkdir(parents=True, exist_ok=True)
