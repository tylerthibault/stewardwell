from flask_app import db
from flask import flash
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from flask_app.models.chores import Chore
from flask_app.models.rewards import Reward

class Family(db.Model):
    __tablename__ = 'families'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_points = db.Column(db.Integer, default=0)  # Family points for rewards
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = db.relationship('FamilyMember', back_populates='family', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', back_populates='family', cascade='all, delete-orphan')
    chores = db.relationship('Chore', back_populates='family', cascade='all, delete-orphan')
    rewards = db.relationship('Reward', back_populates='family', cascade='all, delete-orphan')

    @classmethod
    def create(cls, name):
        try:
            new_family = cls(name=name)
            db.session.add(new_family)
            db.session.commit()
            return new_family
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating family: " + str(e), "danger")
            return None

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    def add_points(self, points):
        """Add points to family total"""
        try:
            self.total_points += points
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error adding points: " + str(e), "danger")
            return False

    def use_points(self, points):
        """Use points from family total"""
        if self.total_points < points:
            flash("Not enough family points", "danger")
            return False
        
        try:
            self.total_points -= points
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error using points: " + str(e), "danger")
            return False