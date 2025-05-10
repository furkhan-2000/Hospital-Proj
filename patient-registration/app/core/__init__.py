from flask import Blueprint

# Define blueprint
bp = Blueprint("core", __name__, url_prefix="/api")

# Register routes (must be after bp is defined)
from . import routes
