from .models import User, TaskPriority, TaskStatus
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Password", validators=[EqualTo("password"), DataRequired()])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please choose a different username")
        

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("Please choose a different email address")
        

class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Edit")

class NewTaskForm(FlaskForm):
    name = StringField("Task Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    priority = SelectField("Priority", choices=[(priority.name, priority.value) for priority in TaskPriority], validators=[DataRequired()])
    submit = SubmitField("Add Task")


class EditTaskForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    status = SelectField('Status', choices=[(status.name, status.value) for status in TaskStatus], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[(priority.name, priority.value) for priority in TaskPriority], validators=[DataRequired()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])