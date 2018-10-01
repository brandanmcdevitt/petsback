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

    def __init__(self, user_id):
        self.user_id = user_id

    # def __repr__(self):
    #     return '<Username %r>' % self.username