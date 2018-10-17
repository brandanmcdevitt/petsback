from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, Form, IntegerField, SelectField, DateTimeField, FileField
from wtforms.validators import DataRequired
import datetime

class RegistrationForm(FlaskForm):
    """Registration form"""

    username = StringField('Username', [validators.Length(min=4, max=12)])
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

    #TODO: add validation to all fields

    forename = StringField('Forename')
    surname = StringField('Surname')
    address = StringField('Address')
    postcode = StringField('Postcode')
    number = IntegerField('Contact Number')
    submit = SubmitField('Update Info')

class ReportLost(FlaskForm):
    """Report lost pet"""

    #TODO: add validators to all fields

    image = FileField('Image File')
    name = StringField('Name of pet')
    age = IntegerField('Pets age')
    colour = StringField('Colour')
    sex = StringField('Sex')
    breed = StringField('Breed')
    location = StringField('City/Town')
    postcode = StringField('Postcode (e.g. BT45 or CR0)')
    animal = SelectField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('rabbit', 'Rabbit'),
                                  ('bird', 'Bird'), ('horse', 'Horse'), ('other', 'Other')])
    collar = BooleanField('Collar')
    chipped = BooleanField('Chipped')
    neutered = BooleanField('Neutered')
    #TODO: fix datetime so that it is clickable calendar view
    missing_since = DateTimeField('Select the date that your pet went missing',
                                  format="%d-%m-%Y %H:%M",
                                  default=datetime.datetime.now())
    submit = SubmitField('Submit')

class ReportFound(FlaskForm):
    """Report found pet"""

    #TODO: add validators to all fields

    image = FileField('Image File')
    colour = StringField('Colour')
    sex = StringField('Sex')
    breed = StringField('Breed')
    location = StringField('City/Town')
    postcode = StringField('Postcode')
    animal = SelectField(choices=[('dog', 'Dog'), ('cat', 'Cat'), ('rabbit', 'Rabbit'),
                                  ('bird', 'Bird'), ('horse', 'Horse'), ('other', 'Other')])
    collar = BooleanField('Collar')
    chipped = BooleanField('Chipped')
    neutered = BooleanField('Neutered')
    #TODO: fix datetime so that it is clickable calendar view
    date_found = DateTimeField('Date pet was found', default=datetime.datetime.now())
    submit = SubmitField('Submit')