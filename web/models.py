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

class Posts(db.Model):
    __tablename__ = "posts"
    post_id = db.Column(db.Integer, primary_key=True)
    refNo = db.Column(db.String(40))
    title = db.Column(db.String(250))
    name = db.Column(db.String(80))
    age = db.Column(db.Integer)
    colour = db.Column(db.String(40))
    gender = db.Column(db.String(40))
    breed = db.Column(db.String(80))
    status = db.Column(db.String(20))
    location = db.Column(db.String(40))
    postcode = db.Column(db.String(40))
    animal_type = db.Column(db.String(50))
    collar = db.Column(db.Boolean, default=False)
    chipped = db.Column(db.Boolean, default=False)
    neutered = db.Column(db.Boolean, default=False)
    missingSince = db.Column(db.DateTime)
    postDate = db.Column(db.DateTime)

    def __init__(self, refNo, title, name, age, colour, gender, breed, status, location, postcode,  
                animal_type, collar, chipped, neutered, missingSince, postDate):
        self.refNo = refNo
        self.title = title
        self.name = name
        self.age = age
        self.colour = colour
        self.gender = gender
        self.breed = breed
        self.status = status
        self.location = location
        self.postcode = postcode
        self.animal_type = animal_type
        self.collar = collar
        self.chipped = chipped
        self.neutered = neutered
        self.missingSince = missingSince
        self.postDate = postDate

    # def __repr__(self):
    #     return '<Username %r>' % self.username