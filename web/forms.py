from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, Form, IntegerField, SelectField, DateTimeField, FileField
from wtforms.validators import DataRequired
import datetime

class RegistrationForm(FlaskForm):
    """Registration form"""

    username = StringField('Username', validators=[validators.Length(min=4, max=12), DataRequired("Enter a username")],
                           render_kw={"placeholder": "Username"})
    email = StringField('Email Address', [validators.Length(min=6, max=35)],
                        render_kw={"placeholder": "Email"})
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')],
                             render_kw={"placeholder": "Password"})
    confirm = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField('Email Address', validators=[DataRequired("Enter your email")],
                           render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[DataRequired("Enter your password")],
                             render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign In')

class UpdateContactInformation(FlaskForm):
    """Create and update contact info for user"""

    #TODO: add validators to all fields

    forename = StringField('First Name')
    surname = StringField('Last Name')
    number = IntegerField('Contact Number')
    address = StringField('Address')
    city = StringField('City/Town')
    postcode = StringField('Postcode')
    submit = SubmitField('Submit')

class ReportLost(FlaskForm):
    """Report lost pet"""

    #TODO: add validators to all fields

    image = FileField('Photo of pet')
    name = StringField('Name of pet', validators=[DataRequired("Enter your email")])
    age = IntegerField('Pets age')
    colour = StringField('Colour')
    sex = SelectField(choices=[('Male', 'Male'), ('Female', 'Female')])
    breed = StringField('Breed')
    location = StringField('City/Town', validators=[DataRequired("Enter your email")])
    postcode = StringField('Postcode (e.g. BT45 or CR0)', validators=[DataRequired("Enter your email")])
    animal = SelectField(choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Rabbit', 'Rabbit'),
                                  ('Bird', 'Bird'), ('Horse', 'Horse'), ('Other', 'Other')])
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
    sex = SelectField(choices=[('Male', 'Male'), ('Female', 'Female')])
    breed = StringField('Breed')
    location = StringField('City/Town', validators=[DataRequired("Enter your email")])
    postcode = StringField('Postcode', validators=[DataRequired("Enter your email")])
    animal = SelectField(choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Rabbit', 'Rabbit'),
                                  ('Bird', 'Bird'), ('Horse', 'Horse'), ('Other', 'Other')])
    collar = BooleanField('Collar')
    chipped = BooleanField('Chipped')
    neutered = BooleanField('Neutered')
    #TODO: fix datetime so that it is clickable calendar view
    date_found = DateTimeField('Date pet was found', default=datetime.datetime.now())
    submit = SubmitField('Submit')

class ResgisterPet(FlaskForm):
    """Register a pet to the system"""

    #TODO: Add validators to all fields and update forms

    image = FileField('Image File')
    name = StringField('Name', validators=[DataRequired("Enter your email")])
    colour = StringField('Colour')
    sex = SelectField(choices=[('Male', 'Male'), ('Female', 'Female')])
    breed = StringField('Breed')
    location = StringField('City/Town', validators=[DataRequired("Enter your email")])
    postcode = StringField('Postcode', validators=[DataRequired("Enter your email")])
    animal = SelectField(choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Rabbit', 'Rabbit'),
                                  ('Bird', 'Bird'), ('Horse', 'Horse'), ('Other', 'Other')])
    submit = SubmitField('Submit')


class ResetPassword(FlaskForm):
    """Reset Password form"""

    email = StringField('Email Address', validators=[DataRequired("Enter your email")],
                           render_kw={"placeholder": "Email"})
    submit = SubmitField('Reset')

class ContactForm(FlaskForm):
    """Contact Form"""

    name = StringField('Name')
    email = StringField('Email')
    number = IntegerField('Phone')
    query = StringField('Message')

    submit = SubmitField('Submit')