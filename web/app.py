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
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.secret_key = b'{S\xfd\xe7\xe0\\\xe1=\xfef8\xac\xcb\xc3\xbd0'

# Create our database model
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

    # def __repr__(self):
    #     return '<Username %r>' % self.username

# Set "homepage" to index.html
@app.route('/')
def index():
    if session.get['user_id'] is None:
        user_id = session['user_id']
        rows = User.query.filter(User.id == user_id).first()
        username = rows.username
        loggedIn = True

        return render_template('index.html', username=username, loggedIn=loggedIn)
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

        #bundle the usernam, email and password
        reg = User(request.form.get('username'), request.form.get('email'), password)
        #add the information thats ready to commit
        db.session.add(reg)
        #commit the data to the database
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

        count = User.query.filter(User.username == request.form.get('username')).count()
        rows = User.query.filter(User.username == request.form.get('username')).first()

        if count != 1 or not check_password_hash(rows.hash, request.form.get('password')):
            invalidEntry = "Incorrect username/password"
            return render_template('login.html', error=invalidEntry)

        session['user_id'] = rows.id

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


if __name__ == "__main__":
    app.debug = True
    app.run()
