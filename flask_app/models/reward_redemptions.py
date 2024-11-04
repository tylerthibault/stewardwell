from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import flash

class RewardRedemption(db.Model):
    __tablename__ = 'reward_redemptions'

    id = db.Column(db.Integer, primary_key=True)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reward = db.relationship('Reward', back_populates='redemptions')
    user = db.relationship('User', back_populates='reward_redemptions')

    @classmethod
    def create(cls, **data):
        try:
            new_redemption = cls(**data)
            db.session.add(new_redemption)
            db.session.commit()
            return new_redemption
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating redemption: " + str(e), "danger")
            return None

    def approve(self):
        """Approve a reward redemption and deduct coins/points"""
        if self.status != 'pending':
            return False

        try:
            if self.reward.is_family_reward:
                # Deduct family points
                success = self.reward.family.use_points(self.reward.points_required)
            else:
                # Deduct user coins
                success = self.user.use_coins(self.reward.coin_cost)

            if success:
                self.status = 'approved'
                db.session.commit()
                return True
            return False

        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error approving redemption: " + str(e), "danger")
            return False 