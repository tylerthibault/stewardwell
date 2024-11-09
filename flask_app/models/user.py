from flask_app import db
from flask_login import UserMixin
from datetime import datetime
import random
import string
from flask_app.utils.logger import get_logger

logger = get_logger()

def generate_family_code():
    """Generate a 6-character family code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class ModuleSettings(db.Model):
    __tablename__ = 'module_settings'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(50), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Remove duplicate backref definition
    family = db.relationship('Family')

    __table_args__ = (
        db.UniqueConstraint('module_name', 'family_id', name='unique_module_per_family'),
    )

class Family(db.Model):
    __tablename__ = 'family'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    family_code = db.Column(db.String(6), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('User', backref='family', lazy=True)
    chores = db.relationship('Chore', backref='family', lazy=True)
    module_settings = db.relationship('ModuleSettings', backref='family_settings', lazy=True)
    goals = db.relationship('Goal', back_populates='family', lazy=True)
    goal_categories = db.relationship('GoalCategory', back_populates='family', lazy=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
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

    # Avatar
    avatar = db.Column(db.String(50), default='fa-user-circle')

    # Chore relationships
    assigned_chores = db.relationship('Chore', 
                                    foreign_keys='Chore.assigned_to_id',
                                    back_populates='assigned_to',
                                    lazy=True)
    created_chores = db.relationship('Chore',
                                   foreign_keys='Chore.created_by_id',
                                   back_populates='created_by',
                                   lazy=True)
    
    # Goal relationships
    created_goals = db.relationship('Goal', back_populates='created_by', lazy=True)
    created_goal_categories = db.relationship('GoalCategory', back_populates='created_by', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

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

class RewardCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default="#6c757d")  # Hex color code
    icon = db.Column(db.String(50))  # FontAwesome icon name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Family relationship
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    rewards = db.relationship('Reward', backref='category', lazy='dynamic')
    created_by = db.relationship('User', foreign_keys=[created_by_id])

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Integer, nullable=False)  # Cost in coins
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add category relationship
    category_id = db.Column(db.Integer, db.ForeignKey('reward_category.id'))
    
    # Family relationship
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    family = db.relationship('Family', backref='rewards')
    
    # Redemption tracking
    redemptions = db.relationship('RewardRedemption', backref='reward', lazy='dynamic')

class RewardRedemption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, denied
    cost = db.Column(db.Integer, nullable=False)  # Store cost at time of redemption
    
    # Relationships
    user = db.relationship('User', backref='reward_redemptions')

class GoalCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#6c757d')  # Hex color code
    icon = db.Column(db.String(50), default='fa-star')
    
    # Foreign Keys
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    family = db.relationship('Family', back_populates='goal_categories')
    created_by = db.relationship('User', back_populates='created_goal_categories')
    goals = db.relationship('Goal', back_populates='category', cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Update the Goal model to include category
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_required = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Foreign Keys
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('goal_category.id'))
    
    # Relationships
    family = db.relationship('Family', back_populates='goals')
    created_by = db.relationship('User', back_populates='created_goals')
    category = db.relationship('GoalCategory', back_populates='goals')