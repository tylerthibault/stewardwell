from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import flash

class Chore(db.Model):
    __tablename__ = 'chores'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coin_value = db.Column(db.Integer, default=0)  # Individual coins earned
    family_points = db.Column(db.Integer, default=0)  # Points toward family goals
    deadline = db.Column(db.DateTime)
    recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))  # daily, weekly, monthly
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = db.relationship('Family', back_populates='chores')
    assignments = db.relationship('ChoreAssignment', back_populates='chore', cascade='all, delete-orphan')

    @classmethod
    def create(cls, **data):
        try:
            new_chore = cls(**data)
            db.session.add(new_chore)
            db.session.commit()
            return new_chore
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating chore: " + str(e), "danger")
            return None 