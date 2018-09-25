from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField, widgets
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AnswerForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField()


class UpdateQuizForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    subjects = MultiCheckboxField('Subjects', coerce=int)
    questions = MultiCheckboxField('Questions', coerce=int)
    submit = SubmitField()
