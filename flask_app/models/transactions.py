from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import flash

class BudgetTransaction(db.Model):
    __tablename__ = 'budget_transactions'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('budget_categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    budget = db.relationship('Budget', back_populates='transactions')
    category = db.relationship('BudgetCategory', back_populates='transactions')
    user = db.relationship('User', back_populates='transactions')

    @classmethod
    def create(cls, **data):
        try:
            new_transaction = cls(**data)
            db.session.add(new_transaction)
            db.session.commit()
            
            # Update budget total
            new_transaction.budget.calculate_total()
            return new_transaction
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating transaction: " + str(e), "danger")
            return None 