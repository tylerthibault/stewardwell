from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)  # Made nullable for child accounts
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # User type
    user_type = db.Column(db.String(20), nullable=False)  # 'parent' or 'child'
    
    # Family relationships
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'))
    
    # Parent-specific relationships
    managed_families = db.relationship(
        'Family',
        backref=db.backref('owner', lazy='joined'),
        lazy='dynamic',
        foreign_keys='Family.owner_id'
    )
    
    # Child-specific relationships
    coins = db.Column(db.Integer, default=0)
    completed_chores = db.relationship(
        'CompletedChore',
        backref='child',
        lazy='dynamic',
        foreign_keys='CompletedChore.child_id'
    )
    verified_chores = db.relationship(
        'CompletedChore',
        backref='verified_by',
        lazy='dynamic',
        foreign_keys='CompletedChore.verified_by_id'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def is_parent(self):
        return self.user_type == 'parent'

    @property
    def is_child(self):
        return self.user_type == 'child'

    def can_access_admin(self):
        return self.is_admin and self.is_active

    def get_completed_chores_count(self):
        return self.completed_chores.filter_by(verified=True).count()

    def get_total_points_contributed(self):
        total = 0
        verified_chores = self.completed_chores.filter_by(verified=True).all()
        for chore in verified_chores:
            total += chore.chore.points_reward
        return total

class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_points = db.Column(db.Integer, default=0)
    
    # Family relationships
    members = db.relationship(
        'User',
        backref=db.backref('family', lazy='joined'),
        lazy='dynamic',
        foreign_keys='User.family_id'
    )
    chores = db.relationship('Chore', backref='family', lazy='dynamic')
    rewards = db.relationship('Reward', backref='family', lazy='dynamic')
    goals = db.relationship('Goal', backref='family', lazy='dynamic')

    def add_points(self, points):
        self.total_points += points
        db.session.commit()

    def get_active_children(self):
        return self.members.filter_by(user_type='child', is_active=True).all()

    def get_total_chores_completed(self):
        total = 0
        for member in self.get_active_children():
            total += member.get_completed_chores_count()
        return total

    def __repr__(self):
        return f'<Family {self.name}>'
