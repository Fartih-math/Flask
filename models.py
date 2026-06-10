from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='customer')  # 'customer' or 'admin'
    sessions = db.relationship('BorrowSession', backref='user', lazy=True)

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, default=0)      # total quantity available
    # no brand field per your request

class BorrowSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.now)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    return_status = db.Column(db.String(50), nullable=True)   # 'normal', 'missing', 'damaged'
    return_note = db.Column(db.Text, nullable=True)
    qr_token = db.Column(db.String(100), unique=True, nullable=False)
    items = db.relationship('BorrowItem', backref='session', lazy=True, cascade='all, delete-orphan')

class BorrowItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('borrow_session.id'), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    equipment = db.relationship('Equipment')
