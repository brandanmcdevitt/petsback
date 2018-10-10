from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, Form
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    """Registration form"""

    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField('Username', validators=[DataRequired("Enter your username")],
                           grender_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired("Enter your password")]
                            grender_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')
