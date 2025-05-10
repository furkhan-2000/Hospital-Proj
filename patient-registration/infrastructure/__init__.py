import structlog
from flask_migrate import upgrade
from app import create_app, db

def run_migrations():
    app = create_app()
    with app.app_context():
        upgrade()
        db.session.execute("PRAGMA journal_mode=WAL;")
        print("Database migrations applied successfully")

if __name__ == "__main__":
    run_migrations()
