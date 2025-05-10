from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback
import structlog

logger = structlog.get_logger()

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        logger.error(
            "HTTP Error",
            error_code=error.code,
            error_name=error.name,
            description=error.description
        )
        return jsonify({
            "error": error.name,
            "message": error.description,
            "status": error.code
        }), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        logger.critical(
            "Unhandled Exception",
            error=str(error),
            stack_trace=traceback.format_exc()
        )
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status": 500
        }), 500
