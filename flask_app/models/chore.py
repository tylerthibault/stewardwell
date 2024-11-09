from flask_app.extensions import db
from datetime import datetime

class Chore(db.Model):
    __tablename__ = 'chores'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('chore_category.id'), nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    category = db.relationship('ChoreCategory', backref='chores')
    assigned_to = db.relationship(
        'User',
        foreign_keys=[assigned_to_id],
        backref=db.backref('assigned_chores', lazy='dynamic')
    )

    def __repr__(self):
        return f'<Chore {self.title}>'

    def complete_chore(self):
        """Mark chore as completed and award points"""
        try:
            self.completed = True
            self.updated_at = datetime.utcnow()
            
            # Award points to the assigned user
            if self.assigned_to:
                self.assigned_to.family_points += self.points
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False