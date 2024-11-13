from app import db
from datetime import datetime

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Appearance Settings
    theme = db.Column(db.String(20), default='light')  # light, dark, system
    color_scheme = db.Column(db.String(20), default='blue')  # blue, green, purple, orange
    font_size = db.Column(db.String(20), default='medium')  # small, medium, large
    density = db.Column(db.String(20), default='comfortable')  # compact, comfortable, spacious
    enable_animations = db.Column(db.Boolean, default=True)
    reduce_motion = db.Column(db.Boolean, default=False)

    # Notification Settings
    email_chores = db.Column(db.Boolean, default=True)
    email_rewards = db.Column(db.Boolean, default=True)
    email_goals = db.Column(db.Boolean, default=True)
    inapp_chores = db.Column(db.Boolean, default=True)
    inapp_rewards = db.Column(db.Boolean, default=True)
    inapp_goals = db.Column(db.Boolean, default=True)
    notification_frequency = db.Column(db.String(20), default='immediately')  # immediately, daily, weekly
    quiet_hours_start = db.Column(db.Time)
    quiet_hours_end = db.Column(db.Time)

    # Email Settings
    email_updates = db.Column(db.Boolean, default=True)
    activity_notifications = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<UserSettings {self.user_id}>'

    @staticmethod
    def get_or_create(user_id):
        """Get existing settings or create new ones for a user"""
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = UserSettings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        return settings

    def update_appearance(self, preferences):
        """Update appearance settings"""
        self.theme = preferences.get('theme', self.theme)
        self.color_scheme = preferences.get('color_scheme', self.color_scheme)
        self.font_size = preferences.get('font_size', self.font_size)
        self.density = preferences.get('density', self.density)
        self.enable_animations = preferences.get('enable_animations', self.enable_animations)
        self.reduce_motion = preferences.get('reduce_motion', self.reduce_motion)
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def update_notifications(self, preferences):
        """Update notification settings"""
        self.email_chores = preferences.get('email_chores', self.email_chores)
        self.email_rewards = preferences.get('email_rewards', self.email_rewards)
        self.email_goals = preferences.get('email_goals', self.email_goals)
        self.inapp_chores = preferences.get('inapp_chores', self.inapp_chores)
        self.inapp_rewards = preferences.get('inapp_rewards', self.inapp_rewards)
        self.inapp_goals = preferences.get('inapp_goals', self.inapp_goals)
        self.notification_frequency = preferences.get('notification_frequency', self.notification_frequency)
        
        if 'quiet_hours_start' in preferences:
            self.quiet_hours_start = preferences['quiet_hours_start']
        if 'quiet_hours_end' in preferences:
            self.quiet_hours_end = preferences['quiet_hours_end']
            
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def update_email_preferences(self, preferences):
        """Update email preferences"""
        self.email_updates = preferences.get('email_updates', self.email_updates)
        self.activity_notifications = preferences.get('activity_notifications', self.activity_notifications)
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def get_appearance_settings(self):
        """Get appearance settings as a dictionary"""
        return {
            'theme': self.theme,
            'color_scheme': self.color_scheme,
            'font_size': self.font_size,
            'density': self.density,
            'enable_animations': self.enable_animations,
            'reduce_motion': self.reduce_motion
        }

    def get_notification_settings(self):
        """Get notification settings as a dictionary"""
        return {
            'email_chores': self.email_chores,
            'email_rewards': self.email_rewards,
            'email_goals': self.email_goals,
            'inapp_chores': self.inapp_chores,
            'inapp_rewards': self.inapp_rewards,
            'inapp_goals': self.inapp_goals,
            'notification_frequency': self.notification_frequency,
            'quiet_hours_start': self.quiet_hours_start,
            'quiet_hours_end': self.quiet_hours_end
        }

    def get_email_preferences(self):
        """Get email preferences as a dictionary"""
        return {
            'email_updates': self.email_updates,
            'activity_notifications': self.activity_notifications
        }
