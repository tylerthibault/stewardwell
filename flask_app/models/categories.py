from flask_app import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = db.relationship('Family', backref='categories')
    chores = db.relationship('Chore', backref='category', lazy=True)

    @classmethod
    def create(cls, **data):
        try:
            category = cls(**data)
            db.session.add(category)
            db.session.commit()
            return category
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_by_family(cls, family_id):
        """Get all categories for a family"""
        return cls.query.filter_by(family_id=family_id).order_by(cls.name).all() 