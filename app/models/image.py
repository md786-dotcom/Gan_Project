from datetime import datetime
from app import db
import json

class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(500), nullable=False)
    s3_url = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    transformations = db.Column(db.Text)  # JSON string of applied transformations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_transformations(self, transformations_dict):
        """Set transformations as JSON string."""
        self.transformations = json.dumps(transformations_dict) if transformations_dict else None
    
    def get_transformations(self):
        """Get transformations as dictionary."""
        return json.loads(self.transformations) if self.transformations else {}
    
    def to_dict(self):
        """Convert image object to dictionary."""
        return {
            'id': self.id,
            'original_name': self.original_name,
            'filename': self.filename,
            's3_url': self.s3_url,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'transformations': self.get_transformations(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Image {self.filename}>'