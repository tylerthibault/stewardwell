from app import db
from flask_login import UserMixin
from datetime import datetime
import random
import string

def generate_family_code():
    """Generate a 6-character family code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    pin = db.Column(db.String(4))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User type flags
    is_superuser = db.Column(db.Boolean, default=False)
    is_parent = db.Column(db.Boolean, default=False)
    
    # Family relationships
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    
    # Parent-child relationship
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    children = db.relationship('User', backref=db.backref('parent', remote_side=[id]))
    
    # Wallet
    coins = db.Column(db.Integer, default=0)
    family_points = db.Column(db.Integer, default=0)

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    family_code = db.Column(db.String(6), unique=True, nullable=False, default=generate_family_code)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('User', backref='family')
    goals = db.relationship('FamilyGoal', backref='family', lazy='dynamic')
    chores = db.relationship('Chore', backref='family', lazy='dynamic')

class FamilyGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_required = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Family relationship
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)

class FamilyJoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='join_requests')
    family = db.relationship('Family', backref='join_requests')

class ChoreCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default="#6c757d")  # Hex color code
    icon = db.Column(db.String(50))  # FontAwesome icon name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Family relationship
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    chores = db.relationship('Chore', backref='category', lazy='dynamic')
    created_by = db.relationship('User', foreign_keys=[created_by_id])

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coins = db.Column(db.Integer, default=0)  # Individual reward
    points = db.Column(db.Integer, default=0)  # Family points
    frequency = db.Column(db.String(20))  # daily, weekly, monthly
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add category relationship
    category_id = db.Column(db.Integer, db.ForeignKey('chore_category.id'))
    
    # Existing relationships
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref='assigned_chores')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_chores')
    
    status = db.Column(db.String(20), default='pending')  # pending, completed, overdue
    completed_at = db.Column(db.DateTime)