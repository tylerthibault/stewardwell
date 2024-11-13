from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[Optional(), Email()])
    family_name = StringField('Family Name', validators=[Optional(), Length(min=2, max=64)])
    email_updates = BooleanField('Receive email updates')
    activity_notifications = BooleanField('Receive activity notifications')

class SecurityForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])

class NotificationForm(FlaskForm):
    email_chores = BooleanField('Chore Updates')
    email_rewards = BooleanField('Reward Updates')
    email_goals = BooleanField('Goal Progress')
    inapp_chores = BooleanField('Chore Notifications')
    inapp_rewards = BooleanField('Reward Notifications')
    inapp_goals = BooleanField('Goal Notifications')
    notification_frequency = SelectField('Email Digest Frequency', choices=[
        ('immediately', 'Immediately'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest')
    ])
    quiet_hours_start = TimeField('Quiet Hours Start', validators=[Optional()])
    quiet_hours_end = TimeField('Quiet Hours End', validators=[Optional()])

class AppearanceForm(FlaskForm):
    theme = SelectField('Theme', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System')
    ])
    color_scheme = SelectField('Color Scheme', choices=[
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('purple', 'Purple'),
        ('orange', 'Orange')
    ])
    font_size = SelectField('Font Size', choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large')
    ])
    density = SelectField('Layout Density', choices=[
        ('compact', 'Compact'),
        ('comfortable', 'Comfortable'),
        ('spacious', 'Spacious')
    ])
    enable_animations = BooleanField('Enable Animations')
    reduce_motion = BooleanField('Reduce Motion')
