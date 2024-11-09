from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

class ChoreForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    points = IntegerField('Points', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    assigned_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    due_date = DateField('Due Date', validators=[Optional()])
    submit = SubmitField('Create Chore')