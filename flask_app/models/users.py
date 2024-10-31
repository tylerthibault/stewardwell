import re
import secrets
from flask_app import db, bcrypt
from flask import flash
from sqlalchemy.exc import SQLAlchemyError

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Password is hashed, so set to a larger length
    session_token = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"


    def __repr__(self):
        return f"<User {self.name}>"

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

