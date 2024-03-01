from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin,db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'participant' or 'admin'
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)

    def __init__(self, email, password_hash, user_type):
        self.email = email
        self.password_hash = password_hash
        self.user_type = user_type

    def check_password(hash, password_hash):
        return hash == password_hash

    def __repr__(self):
        return f'<User {self.email}>'
    



class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    feedback_type = db.Column(db.String(50), nullable=False)  # 'General Query' or 'Challenge Issue'
    challenge_name = db.Column(db.String(120))  # Nullable, only filled for 'Challenge Issue'
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.relationship('Answer', backref='feedback', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback {self.id}>'

class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=False)

    def __repr__(self):
        return f'<Answer {self.id}>'
