from flask import request, jsonify, current_app, render_template
from datetime import datetime
import structlog
from email_validator import validate_email as validate_email_address
from bleach import clean

from sqlalchemy.exc import IntegrityError
from sqlalchemy import text                     # ← NEW IMPORT
from app.extensions import db, limiter, mail
from flask_mail import Message

from . import bp
from .models import Patient

logger = structlog.get_logger()

@bp.route("/patients", methods=["POST"])
@limiter.limit("5/minute")
def create_patient():
    try:
        data = request.get_json(force=True)
        required = ["first_name", "last_name", "date_of_birth", "sex", "email", "phone"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate email format
        validate_email_address(data["email"], check_deliverability=False)

        # Build Patient object
        patient = Patient(
            first_name    = clean(data["first_name"], strip=True),
            last_name     = clean(data["last_name"], strip=True),
            date_of_birth = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date(),
            sex           = data["sex"],
            email         = data["email"].lower().strip(),
            phone         = clean(data["phone"], strip=True),
            description   = clean(data.get("description", ""), strip=True)
        )

        db.session.add(patient)
        db.session.commit()

        logger.info("Patient registered",
                    timestamp=datetime.utcnow().isoformat(),
                    patient_id=patient.id)

        # Send styled HTML email
        doctor_addr = current_app.config["ADMIN_EMAIL"]
        msg = Message(
            subject="New Patient Registration",
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[doctor_addr]
        )
        msg.html = render_template("patient_email.html", patient=patient)
        mail.send(msg)

        return jsonify({"message": "Patient created", "patient_id": patient.id}), 201

    except IntegrityError as e:
        db.session.rollback()
        if "UNIQUE constraint failed: patients.email" in str(e):
            return jsonify({"error": "Email address already exists"}), 400
        return jsonify({"error": "Database integrity error"}), 400

    except Exception as e:
        db.session.rollback()
        logger.error("Patient creation failed", error=str(e))
        return jsonify({"error": str(e)}), 400

@bp.route("/health", methods=["GET"])
def health():
    try:
        # Wrap the raw SQL in text(), otherwise SQLAlchemy 2.x rejects bare strings
        db.session.execute(text("SELECT 1"))      # ← UPDATED LINE
        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({"status": "unhealthy", "error": str(e)}), 500
