from guru_ai.database import db
from datetime import datetime

class UserSageInfo(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    sage_id = db.Column(db.Integer, db.ForeignKey('sage.id'), primary_key=True)
    system_instruction = db.Column(db.Text, nullable=True)
    prompt_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('user_sage_infos', lazy=True))
    sage = db.relationship('Sage', backref=db.backref('user_sage_infos', lazy=True))

    def __repr__(self):
        return f'<UserSageInfo User:{self.user_id} Sage:{self.sage_id}>'

    @classmethod
    def get_user_sage_info(cls, user_id, sage_id) -> "UserSageInfo":
        return cls.query.filter_by(user_id=user_id, sage_id=sage_id).first()

    @classmethod
    def create_or_update_user_sage_info(cls, user_id, sage_id, system_instruction, prompt_text):
        user_sage_info = cls.get_user_sage_info(user_id, sage_id)

        if user_sage_info:
            user_sage_info.system_instruction = system_instruction
            user_sage_info.prompt_text = prompt_text
            user_sage_info.timestamp = datetime.utcnow()
        else:
            user_sage_info = cls(
                user_id=user_id,
                sage_id=sage_id,
                system_instruction=system_instruction,
                prompt_text=prompt_text
            )
            db.session.add(user_sage_info)
        db.session.commit()
        return user_sage_info
