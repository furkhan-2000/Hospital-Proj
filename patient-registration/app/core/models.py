from app.extensions import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = 'patients'

    id            = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String(50), nullable=False)
    last_name     = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    age           = db.Column(db.Integer, nullable=False)
    sex           = db.Column(db.Enum('Male','Female','Other', name='sex_enum'), nullable=False)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    phone         = db.Column(db.String(20), nullable=False)
    description   = db.Column(db.Text, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_email", "email"),
        db.Index("idx_created_at", "created_at"),
        db.CheckConstraint("date_of_birth < CURRENT_DATE", name="valid_dob"),
    )

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"
