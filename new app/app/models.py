from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    profiles = db.relationship('UserProfile', backref='owner', lazy='dynamic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    function_bonus_base_amount = db.Column(db.Float, default=0)
    performance_bonus_amount = db.Column(db.Float, default=0)
    prime_de_niveau_amount = db.Column(db.Float, default=0)
    seniority_rate_percent = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    calculations = db.relationship('CalculationHistory', backref='profile', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<UserProfile {self.name}>'

class CalculationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    input_data = db.Column(db.Text)  # JSON string of inputs
    result_data = db.Column(db.Text)  # JSON string of results
    gross_salary = db.Column(db.Float)
    net_salary = db.Column(db.Float)
    
    def __repr__(self):
        return f'<CalculationHistory {self.id} for profile {self.profile_id}>' 