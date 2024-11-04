import re
import secrets
from flask_app import db, bcrypt
from flask import flash
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    session_token = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    coin_balance = db.Column(db.Integer, default=0)
    pin_code = db.Column(db.String(6))  # For kid's easy login
    is_child = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For linking kids to parents
    settings = db.Column(db.JSON, default=lambda: {
        'module_chores': True,
        'module_budget': True
    })

    # Relationships
    family_memberships = db.relationship('FamilyMember', back_populates='user', cascade='all, delete-orphan')
    transactions = db.relationship('BudgetTransaction', back_populates='user', cascade='all, delete-orphan')
    reward_redemptions = db.relationship('RewardRedemption', back_populates='user', cascade='all, delete-orphan')
    chores_assigned = db.relationship('ChoreAssignment', 
                                    foreign_keys='ChoreAssignment.assigned_to_id',
                                    backref='assigned_to')
    chores_created = db.relationship('ChoreAssignment', 
                                   foreign_keys='ChoreAssignment.assigned_by_id',
                                   backref='assigned_by')
    children = db.relationship('User', 
                             backref=db.backref('parent', remote_side=[id]),
                             foreign_keys='User.parent_id')

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

    # ********* CREATE *********
    @classmethod
    def create_one(cls, **data):
        """Create a new user and add it to the database."""
        data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        del data['confirm_password']
        
        new_user = cls(**data)
        new_user.generate_session_token()

        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating user: " + str(e), "danger")
            return None

    # ********* READ *********
    @classmethod
    def get_all(cls):
        """Retrieve all users from the database."""
        return cls.query.all()

    @classmethod
    def get(cls, **kwargs):
        """Retrieve a specific user by any field, such as ID or session_token."""
        return cls.query.filter_by(**kwargs).first()

    # ********* UPDATE *********
    @classmethod
    def update_one(cls, filter_data, **update_data):
        """Update an existing user in the database."""
        user = cls.query.filter_by(**filter_data).first()
        if not user:
            flash("User not found", "danger")
            return None

        for key, value in update_data.items():
            setattr(user, key, value)
        
        try:
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error updating user: " + str(e), "danger")
            return None

    # ********* DELETE *********
    @classmethod
    def delete_one(cls, id):
        """Delete a specific user by ID."""
        user = cls.query.get(id)
        if not user:
            flash("User not found", "danger")
            return False
        
        try:
            db.session.delete(user)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error deleting user: " + str(e), "danger")
            return False

    # ********* VALIDATION *********
    @staticmethod
    def get_by_email(email):
        """Retrieve a user by email."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def validator(first_name, last_name, email, password, confirm_password):
        """Validate user data for creation and updates."""
        is_valid = True

        # First Name Validation
        if not first_name or len(first_name) < 2:
            flash("First name must be at least 2 characters long", "danger")
            is_valid = False

        # Last Name Validation
        if not last_name or len(last_name) < 2:
            flash("Last name must be at least 2 characters long", "danger")
            is_valid = False

        # Email Validation
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not email or not re.match(email_regex, email):
            flash("Invalid email format", "danger")
            is_valid = False

        # Password Validation
        if not password or len(password) < 8:
            flash("Password must be at least 8 characters long", "danger")
            is_valid = False
        elif not re.search(r'[A-Z]', password):
            flash("Password must contain at least one uppercase letter", "danger")
            is_valid = False
        elif not re.search(r'[a-z]', password):
            flash("Password must contain at least one lowercase letter", "danger")
            is_valid = False
        elif not re.search(r'[0-9]', password):
            flash("Password must contain at least one digit", "danger")
            is_valid = False
        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash("Password must contain at least one special character", "danger")
            is_valid = False

        # Confirm Password Validation
        if password != confirm_password:
            flash("Password and confirm password must match", "danger")
            is_valid = False

        return is_valid

    
    # ********* UTILITIES *********
    def generate_session_token(self):
        """Generate a new unique session token and save it to the database."""
        self.session_token = secrets.token_urlsafe(32)
        db.session.commit()  # Save the new session token to the database
        return self.session_token

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def get_families(self):
        """Get all families this user belongs to"""
        return [membership.family for membership in self.family_memberships]

    def get_primary_family(self):
        """Get the first family this user belongs to (if any)"""
        membership = self.family_memberships[0] if self.family_memberships else None
        return membership.family if membership else None

    def is_parent_in_family(self, family_id):
        """Check if user is a parent in the specified family"""
        membership = next((m for m in self.family_memberships if m.family_id == family_id), None)
        return membership and membership.role == 'parent'

    def add_coins(self, amount):
        """Add coins to user's balance"""
        try:
            self.coin_balance += amount
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error adding coins: " + str(e), "danger")
            return False

    def use_coins(self, amount):
        """Use coins from user's balance"""
        if self.coin_balance < amount:
            flash("Not enough coins", "danger")
            return False
        
        try:
            self.coin_balance -= amount
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error using coins: " + str(e), "danger")
            return False

    def get_pending_chores(self):
        """Get all pending chores assigned to the user"""
        return [assignment for assignment in self.chores_assigned if assignment.status == 'pending']

    def get_completed_chores(self):
        """Get all completed chores by the user"""
        return [assignment for assignment in self.chores_assigned if assignment.status == 'completed']

    def get_approved_chores(self):
        """Get all approved chores by the user"""
        return [assignment for assignment in self.chores_assigned if assignment.status == 'approved']

    def switch_to_child(self, child_id):
        """For parents to switch to child view"""
        if not self.is_parent_in_family(family_id):
            return False
        
        child = User.query.get(child_id)
        if not child or child.parent_id != self.id:
            return False
        
        return child

    @classmethod
    def verify_pin(cls, email, pin):
        """Verify child's PIN code"""
        user = cls.query.filter_by(email=email, pin_code=pin, is_child=True).first()
        return user

    def get_managed_children(self):
        """Get all children managed by this parent"""
        return User.query.filter_by(parent_id=self.id).all()

    def update_settings(self, **settings):
        """Update user settings"""
        try:
            self.settings.update(settings)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error updating settings: " + str(e), "danger")
            return False

