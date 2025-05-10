from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/day", "50/hour"])
mail = Mail()
