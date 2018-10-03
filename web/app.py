#import secret
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
#importing heroku to connect with my postgres database
from flask_heroku import Heroku
from helpers import login_required

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/management'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

#import data model from models.py
from models import User, Contact, Posts

#TODO: hide key with heroku import 
app.secret_key = b'{S\xfd\xe7\xe0\\\xe1=\xfef8\xac\xcb\xc3\xbd0'

#set homepage to index.html and personalise content
@app.route('/')
def index():
    """homepage"""

    #if 'user_id' exists within the session return index.html and pass in username
    if session.get("user_id") is not None:
        user_id = session['user_id']
        rows = User.query.filter(User.id == user_id).first()
        username = rows.username
        loggedIn = True

        return render_template('index.html', username=username, loggedIn=loggedIn)
    
    #else return index.html
    else:
        loggedIn = False
        return render_template('index.html', loggedIn=loggedIn)


# Register new users and redirect to index
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""

    #forget any previously stored user_id
    session.clear()

    #if user reached this page via POST
    if request.method == 'POST':

        #ensure a username was submitted
        if not request.form.get('username'):
            emptyUsername = "No username submitted"
            return render_template('register.html', error=emptyUsername)
        #ensure email was submitted
        elif not request.form.get('email'):
            emptyEmail = "No email submitted"
            return render_template('register.html', error=emptyEmail)
        elif "@" not in request.form.get('email'):
            emailFormat = "Incorrect email format"
            return render_template('register.html', error=emailFormat)
        #ensure a password was submitted
        elif not request.form.get('password') or not request.form.get('confirmation'):
            emptyPassword = "No password submitted"
            return render_template('register.html', error=emptyPassword)

        #ensure that the username and email doesn't already exist in the database
        rows = User.query.all()
        for user in rows:
            if request.form.get('username').lower() == user.username.lower():
                usernameExists = "Username already exists"
                return render_template('register.html', error=usernameExists)
            elif request.form.get('email').lower() == user.email.lower():
                emailExists = "Email address already registered"
                return render_template('register.html', error=emailExists)

        #ensure that the passwords match
        if request.form.get('password') != request.form.get('confirmation'):
            noMatch = "Passwords do not match"
            return render_template('register.html', error=noMatch)
        #else hash password for security
        else:
            password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

        #bundle the username, email and password
        reg = User(request.form.get('username'), request.form.get('email'), password)
        #add the information thats ready to commit
        db.session.add(reg)
        #commit the data to the database
        db.session.commit()

        #query database and set the session 'user_id' to user.id
        user = User.query.filter(User.username == request.form.get('username')).first()
        session['user_id'] = user.id

        #update contact table
        contact = Contact(user.id, "?", "?", "?", "?", "000")
        db.session.add(contact)
        db.session.commit()

        #redirect the user to the homepage upon successful completion
        return redirect('/')

    #else if the user reached this page via GET
    else:
         return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""

    #forget any previously stored user_id
    session.clear()

    #if user reached this page via POST
    if request.method == 'POST':

        #ensure that a username was submitted
        if not request.form.get('username'):
            emptyUsername = "No username submitted"
            return render_template('login.html', error=emptyUsername)

        #ensure the password was submitted
        elif not request.form.get('password'):
            emptyPassword = "No password submitted"
            return render_template('login.html', error=emptyPassword)

        #return either 1 or 0 if the username exists
        #TODO: fix case sensitivity
        count = User.query.filter(User.username == request.form.get('username')).count()
        #query the database for user details
        user = User.query.filter(User.username == request.form.get('username')).first()

        #if the count is not 1 and the password doesnt match the input, throw error
        if count != 1 or not check_password_hash(user.hash, request.form.get('password')):
            invalidEntry = "Incorrect username/password"
            return render_template('login.html', error=invalidEntry)

        session['user_id'] = user.id

        return redirect('/')
    
    #else if the user reached this page via GET
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to index
    return redirect("/")

@app.route("/account/update-info", methods=['GET', 'POST'])
@login_required
def update():
    """Update contact info"""
    #TODO: add validation to form, comments and auto fill form upon completion with stored data

    user_id = session['user_id']
    rows = User.query.filter(User.id == user_id).first()
    username = rows.username
    email = rows.email

    if request.method == 'POST':

        forename = request.form.get('forename')
        surname = request.form.get('surname')
        address = request.form.get('address')
        postcode = request.form.get('postcode')
        number = request.form.get('number')

        contact = Contact.query.filter(Contact.user_id == user_id).first()
        contact.surname = surname
        contact.forename = forename
        contact.address = address
        contact.postcode = postcode
        contact.number = number
        db.session.commit()

        return render_template('update-info.html', username=username, email=email)

    else:
        return render_template('update-info.html', username=username, email=email)

@app.route("/account")
@login_required
def account():
    """User account"""

    return render_template('account.html')

@app.route("/create-post")
@login_required
def create_post():
    """Create post"""

    if request.method == 'POST':
        status = request.form.get('type')
        animal = request.form.get('animal')

        posts = Posts(status, animal)
        db.session.add(posts)
        db.session.commit()

@app.route("/posts")
@login_required
def posts():
    """View posts"""

if __name__ == "__main__":
    app.debug = True
    app.run()
