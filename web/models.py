from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hash = db.Column(db.String(250), unique=False, nullable=False)

    def __init__(self, username, email, hash):
        self.username = username
        self.email = email
        self.hash = hash


class Contact(db.Model):
    __tablename__ = "contact"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True)
    surname = db.Column(db.String(50))
    forename = db.Column(db.String(50))
    address = db.Column(db.String(120))
    postcode = db.Column(db.String(50))
    number = db.Column(db.Integer)
    
    def __init__(self, user_id, surname, forename, address, postcode, number):
        self.user_id = user_id
        self.surname = surname
        self.forename = forename
        self.address = address
        self.postcode = postcode
        self.number = number


class Lost(db.Model):
    """Lost pets table"""
    __tablename__ = "lost"
    post_id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(40))
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    age = db.Column(db.Integer)
    colour = db.Column(db.String(40))
    sex = db.Column(db.String(40))
    breed = db.Column(db.String(80))
    location = db.Column(db.String(40))
    postcode = db.Column(db.String(40))
    animal_type = db.Column(db.String(50))
    collar = db.Column(db.String(10))
    chipped = db.Column(db.String(10))
    neutered = db.Column(db.String(10))
    missing_since = db.Column(db.DateTime)
    post_date = db.Column(db.DateTime)

    def __init__(self, ref_no, user_id, name, age, colour, sex, breed, location, postcode,  
                animal_type, collar, chipped, neutered, missing_since, post_date):
        self.ref_no = ref_no
        self.user_id = user_id
        self.name = name
        self.age = age
        self.colour = colour
        self.sex = sex
        self.breed = breed
        self.location = location
        self.postcode = postcode
        self.animal_type = animal_type
        self.collar = collar
        self.chipped = chipped
        self.neutered = neutered
        self.missing_since = missing_since
        self.post_date = post_date