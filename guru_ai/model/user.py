from guru_ai.database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True) # Nullable for Google users
    name = db.Column(db.String(100), nullable=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True) # New column for profile picture

    def __repr__(self):
        return f'<User {self.email}>'
