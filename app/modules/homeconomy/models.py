from app import db
from datetime import datetime

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    coins_reward = db.Column(db.Integer, nullable=False)
    points_reward = db.Column(db.Integer, nullable=False)
    frequency = db.Column(db.String(20))  # 'daily', 'weekly', 'monthly', 'once'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed_chores = db.relationship('CompletedChore', backref='chore', lazy='dynamic')

    def __repr__(self):
        return f'<Chore {self.name}>'

class CompletedChore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    
    # Relationships
    chore_id = db.Column(db.Integer, db.ForeignKey('chore.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<CompletedChore {self.chore_id} by {self.child_id}>'

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    coin_cost = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=-1)  # -1 means unlimited
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    claimed_rewards = db.relationship('ClaimedReward', backref='reward', lazy='dynamic')

    def __repr__(self):
        return f'<Reward {self.name}>'

class ClaimedReward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claimed_at = db.Column(db.DateTime, default=datetime.utcnow)
    fulfilled = db.Column(db.Boolean, default=False)
    fulfilled_at = db.Column(db.DateTime)
    
    # Relationships
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fulfilled_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<ClaimedReward {self.reward_id} by {self.child_id}>'

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    points_required = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    achieved_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)

    def check_achievement(self, family):
        if not self.achieved_at and family.total_points >= self.points_required:
            self.achieved_at = datetime.utcnow()
            self.is_active = False
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<Goal {self.name}>'
