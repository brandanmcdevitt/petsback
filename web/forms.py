from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, Form, IntegerField, SelectField, DateTimeField, FileField
from wtforms.validators import DataRequired

class RegistrationForm(FlaskForm):
    """Registration form"""

    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField('Username', validators=[DataRequired("Enter your username")],
                           render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired("Enter your password")],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')

class UpdateInfo(FlaskForm):
    """Update user info"""

    #TODO: add validation to this form
    forename = StringField('Forename')
    surname = StringField('Surname')
    address = StringField('Address')
    postcode = StringField('Postcode')
    number = IntegerField('Contact Number')
    submit = SubmitField('Update Info')

class ReportLost(FlaskForm):
    """Report lost dog"""

    image = FileField('Image File', [validators.regexp('^[^/\\]\.jpg$')])
    name = StringField('Name')
    age = IntegerField('Age')
    colour = StringField('Colour')
    sex = StringField('Sex')
    breed = StringField('Breed')
    location = StringField('City/Town')
    postcode = StringField('Postcode')
    animal = SelectField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('rabbit', 'Rabbit'),
                                  ('bird', 'Bird'), ('horse', 'Other')])
    collar = BooleanField('Collar')
    chipped = BooleanField('Chipped')
    neutered = BooleanField('Neutered')
    missing_since = DateTimeField('Date went missing')
