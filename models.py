from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class License(db.Model):
    __tablename__ = "licenses"
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.String(128), unique=True, nullable=False)
    note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
