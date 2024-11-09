from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_login import current_user

class ChoreForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    points = IntegerField('Points', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message="Points must be between 0 and 100")
    ])
    due_date = DateField('Due Date', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ChoreForm, self).__init__(*args, **kwargs)
        
        # Dynamically populate assigned_to choices
        if current_user.is_authenticated and current_user.family:
            children = [(str(child.id), child.username) 
                       for child in current_user.family.members 
                       if not child.is_parent]
            self.assigned_to = SelectField('Assign To', choices=children, validators=[DataRequired()])
            
            # Get categories for this family
            from flask_app.models.user import ChoreCategory
            categories = ChoreCategory.query.filter_by(family_id=current_user.family_id).all()
            category_choices = [(str(cat.id), cat.name) for cat in categories]
            category_choices.insert(0, ('', 'No Category'))  # Add empty choice
            self.category = SelectField('Category', choices=category_choices, validators=[Optional()]) 