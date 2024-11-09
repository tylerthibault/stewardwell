from app import db
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger()

class Chore(db.Model):
    __tablename__ = 'chore'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, verified
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign Keys
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('chore_category.id'), nullable=True)
    
    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], backref=db.backref('assigned_chores', lazy=True))
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref=db.backref('created_chores', lazy=True))

    def __repr__(self):
        return f'<Chore {self.title}>'

    def complete_chore(self):
        """Mark a chore as completed and award points to the assigned user"""
        try:
            if not self.assigned_to:
                logger.error("Cannot complete chore: no user assigned",
                           extra={"chore_id": self.id})
                return False

            if self.status != 'pending':
                logger.warning("Chore already completed or verified",
                             extra={
                                 "chore_id": self.id,
                                 "current_status": self.status
                             })
                return False

            # Update chore status
            self.status = 'completed'
            self.completed_at = datetime.utcnow()

            # Award points to user
            if self.points > 0:
                self.assigned_to.coins += self.points
                self.assigned_to.family_points += self.points

            # Commit changes
            db.session.commit()
            
            logger.info("Chore completed successfully",
                       extra={
                           "chore_id": self.id,
                           "user_id": self.assigned_to_id,
                           "points_awarded": self.points,
                           "new_coin_balance": self.assigned_to.coins,
                           "new_points_balance": self.assigned_to.family_points
                       })
            return True

        except Exception as e:
            db.session.rollback()
            logger.error("Error completing chore",
                        exc_info=True,
                        extra={
                            "chore_id": self.id,
                            "user_id": self.assigned_to_id if self.assigned_to else None,
                            "attempted_points": self.points
                        })
            return False

    def verify_chore(self):
        """Verify a completed chore (parent only)"""
        try:
            if self.status != 'completed':
                logger.warning("Cannot verify: chore not completed",
                             extra={
                                 "chore_id": self.id,
                                 "current_status": self.status
                             })
                return False

            self.status = 'verified'
            db.session.commit()

            logger.info("Chore verified successfully",
                       extra={
                           "chore_id": self.id,
                           "user_id": self.assigned_to_id
                       })
            return True

        except Exception as e:
            db.session.rollback()
            logger.error("Error verifying chore",
                        exc_info=True,
                        extra={
                            "chore_id": self.id,
                            "user_id": self.assigned_to_id if self.assigned_to else None
                        })
            return False