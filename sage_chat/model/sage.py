from sage_chat.database import db

class Sage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    initial_message = db.Column(db.String(500), nullable=False)
    system_instruction = db.Column(db.String(10000), nullable=True)
    response_template = db.Column(db.String(10000), nullable=False)
    portrait_url = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Sage {self.name}>'

    @classmethod
    def get_sage(cls, name) -> "Sage":
        sage = cls.query.filter_by(name=name).first()
        if sage:
            return sage
        # Fallback to Socrates if the requested sage is not found
        return cls.query.filter_by(name="Socrates").first()

    @classmethod
    def get_all_sages(cls):
        return cls.query.all()
