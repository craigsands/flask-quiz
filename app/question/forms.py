from flask_babel import _, lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import BooleanField, SubmitField


class UploadQuizForm(FlaskForm):
    file = FileField(validators=[
        FileRequired(),
        FileAllowed(['xls', 'xlsx'], 'Excel files only!')
    ])
    create_quiz = BooleanField(_l('Create sample quiz?'))
    submit = SubmitField('Import')
