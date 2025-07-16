from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    diary_entries = db.relationship('DiaryEntry', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []