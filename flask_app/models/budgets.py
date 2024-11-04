from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import flash

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = db.relationship('Family', back_populates='budgets')
    categories = db.relationship('BudgetCategory', back_populates='budget', cascade='all, delete-orphan')
    transactions = db.relationship('BudgetTransaction', back_populates='budget', cascade='all, delete-orphan')

    @classmethod
    def create(cls, **data):
        try:
            new_budget = cls(**data)
            db.session.add(new_budget)
            db.session.commit()
            return new_budget
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error creating budget: " + str(e), "danger")
            return None

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    def update(self, **data):
        try:
            for key, value in data.items():
                setattr(self, key, value)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error updating budget: " + str(e), "danger")
            return False

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error deleting budget: " + str(e), "danger")
            return False

    def calculate_total(self):
        """Recalculate total based on all transactions"""
        self.total_amount = sum(t.amount for t in self.transactions)
        db.session.commit() 