from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, Form
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    """Registration form"""

    username = StringField('Username', [validators.Length(min=4, max=25)],
                           validators=[DataRequired("Enter a username")])
    email = StringField('Email Address', [validators.Length(min=6, max=35)],
                        validators=[DataRequired("Enter an email address")])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField('Username', validators=[DataRequired("Enter your username")],
                           render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired("Enter your password")],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')
