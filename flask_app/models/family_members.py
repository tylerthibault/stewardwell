from flask_app import db
from flask import flash
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class FamilyRole:
    PARENT = 'parent'
    CHILD = 'child'
    GUARDIAN = 'guardian'

    @classmethod
    def all_roles(cls):
        return [cls.PARENT, cls.CHILD, cls.GUARDIAN]

class FamilyMember(db.Model):
    __tablename__ = 'family_members'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='family_memberships')
    family = db.relationship('Family', back_populates='members')

    @classmethod
    def create(cls, user_id, family_id, role):
        if role not in FamilyRole.all_roles():
            flash("Invalid role specified", "danger")
            return None
            
        try:
            new_member = cls(user_id=user_id, family_id=family_id, role=role)
            db.session.add(new_member)
            db.session.commit()
            return new_member
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error adding family member: " + str(e), "danger")
            return None 