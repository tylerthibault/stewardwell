from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import flash

class Reward(db.Model):
    __tablename__ = 'rewards'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coin_cost = db.Column(db.Integer, default=0)  # Cost in coins (for individual rewards)
    points_required = db.Column(db.Integer, default=0)  # Required family points (for family rewards)
    is_family_reward = db.Column(db.Boolean, default=False)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = db.relationship('Family', back_populates='rewards')
    redemptions = db.relationship('RewardRedemption', back_populates='reward', cascade='all, delete-orphan')

    @classmethod
    def create(cls, **data):
        try:
            new_reward = cls(**data)
            db.session.add(new_reward)
            db.session.commit()
            return new_reward
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating reward: " + str(e), "danger")
            return None 