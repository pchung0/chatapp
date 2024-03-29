from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from chatapp.models import User


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired(), Length(min=2, max=26)])
    last_name = StringField('Last Name', validators=[InputRequired(), Length(min=2, max=26)])
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=120)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose another one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=120)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')