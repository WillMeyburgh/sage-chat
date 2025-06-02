from guru_ai.database import db
from datetime import datetime

class UserSageInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sage_id = db.Column(db.String(50), nullable=False) # Assuming sage_id is a string, adjust if it's an integer foreign key
    system_information = db.Column(db.Text, nullable=True)
    prompt_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('user_sage_infos', lazy=True))

    def __repr__(self):
        return f'<UserSageInfo User:{self.user_id} Sage:{self.sage_id}>'
