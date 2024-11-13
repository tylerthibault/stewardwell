from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class FamilyForm(FlaskForm):
    name = StringField('Family Name', validators=[DataRequired(), Length(min=2, max=64)])
    submit = SubmitField('Create Family')

class ChoreForm(FlaskForm):
    name = StringField('Chore Name', validators=[DataRequired(), Length(min=2, max=64)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    coins_reward = IntegerField('Coin Reward', validators=[
        DataRequired(),
        NumberRange(min=0, message="Coin reward must be positive")
    ])
    points_reward = IntegerField('Point Reward', validators=[
        DataRequired(),
        NumberRange(min=0, message="Point reward must be positive")
    ])
    frequency = SelectField('Frequency', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('once', 'One Time')
    ])
    assigned_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create Chore')

    def __init__(self, *args, family=None, **kwargs):
        super(ChoreForm, self).__init__(*args, **kwargs)
        if family:
            self.assigned_to.choices = [(0, 'Unassigned')] + [
                (user.id, user.username) 
                for user in family.members.filter_by(user_type='child').all()
            ]

class RewardForm(FlaskForm):
    name = StringField('Reward Name', validators=[DataRequired(), Length(min=2, max=64)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    coin_cost = IntegerField('Coin Cost', validators=[
        DataRequired(),
        NumberRange(min=0, message="Coin cost must be positive")
    ])
    quantity = IntegerField('Quantity (-1 for unlimited)', validators=[
        DataRequired(),
        NumberRange(min=-1, message="Quantity must be -1 or positive")
    ], default=-1)
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create Reward')

class GoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired(), Length(min=2, max=64)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    points_required = IntegerField('Points Required', validators=[
        DataRequired(),
        NumberRange(min=0, message="Points required must be positive")
    ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Create Goal')

class VerifyChoreForm(FlaskForm):
    verified = BooleanField('Verify Completion', default=True)
    submit = SubmitField('Verify Chore')

class ClaimRewardForm(FlaskForm):
    submit = SubmitField('Claim Reward')

class FulfillRewardForm(FlaskForm):
    fulfilled = BooleanField('Mark as Fulfilled', default=True)
    submit = SubmitField('Fulfill Reward')

class AddChildForm(FlaskForm):
    username = StringField('Child Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Child Email', validators=[Optional(), Length(max=120)])
    password = StringField('Initial Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Add Child')

class JoinFamilyForm(FlaskForm):
    family_code = StringField('Family Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Join Family')
