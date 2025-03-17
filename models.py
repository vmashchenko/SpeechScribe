from datetime import datetime
from app import db

class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending, completed, error
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'text': self.text,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
