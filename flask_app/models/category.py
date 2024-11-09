from flask_app.extensions import db
from datetime import datetime

class ChoreCategory(db.Model):
    __tablename__ = 'chore_category'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default="#6c757d")  # Hex color code
    icon = db.Column(db.String(50))  # FontAwesome icon name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    family = db.relationship('Family')
    created_by = db.relationship(
        'User',
        primaryjoin="ChoreCategory.created_by_id==User.id",
        backref='created_chore_categories'
    )
    chores = db.relationship(
        'Chore',
        backref='category',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<ChoreCategory {self.name}>' 