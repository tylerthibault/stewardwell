from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import flash

class ChoreAssignment(db.Model):
    __tablename__ = 'chore_assignments'

    id = db.Column(db.Integer, primary_key=True)
    chore_id = db.Column(db.Integer, db.ForeignKey('chores.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, approved, rejected
    completed_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chore = db.relationship('Chore', back_populates='assignments')

    @classmethod
    def create(cls, **data):
        try:
            new_assignment = cls(**data)
            db.session.add(new_assignment)
            db.session.commit()
            return new_assignment
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating assignment: " + str(e), "danger")
            return None

    def complete(self):
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()

    def approve(self):
        self.status = 'approved'
        self.approved_at = datetime.utcnow()
        db.session.commit()
        # Award coins and points
        self.award_rewards()

    def reject(self):
        self.status = 'rejected'
        db.session.commit()

    def award_rewards(self):
        """Award coins and family points when a chore is approved"""
        if self.status == 'approved':
            # Add coins to user's balance
            self.assigned_to.add_coins(self.chore.coin_value)
            # Add family points
            self.chore.family.add_points(self.chore.family_points)