from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import flash

class BudgetCategory(db.Model):
    __tablename__ = 'budget_categories'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    planned_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    budget = db.relationship('Budget', back_populates='categories')
    transactions = db.relationship('BudgetTransaction', back_populates='category', cascade='all, delete-orphan')

    @property
    def actual_amount(self):
        """Calculate total spent in this category"""
        return sum(t.amount for t in self.transactions)

    @property
    def remaining_amount(self):
        """Calculate remaining budget in this category"""
        return self.planned_amount - self.actual_amount 

    @classmethod
    def create(cls, **data):
        """Create a new budget category"""
        try:
            new_category = cls(**data)
            db.session.add(new_category)
            db.session.commit()
            return new_category
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating category: " + str(e), "danger")
            return None