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

    #query database and pull information
    #>>> db.session.query(User.username).all()

# Set "homepage" to index.html
@app.route('/')
def index():
    user_id = session['user_id']
    rows = User.query.filter(User.id == user_id).first()
    username = rows.username

    return render_template('index.html', username=username)

# Save e-mail to database and send to success page
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""

    #forget any previously stored user_id
    session.clear()

    #if user reached this page via POST
    if request.method == 'POST':

        #rows = db.session.query.

        password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

        reg = User(request.form.get('username'), request.form.get('email'), password)
        db.session.add(reg)
        db.session.commit()

        return redirect('/')

    else:
         return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""

    #forget any previously stored user_id
    session.clear()

    if request.method == 'POST':

        rows = User.query.filter(User.username == request.form.get('username')).first()

        session['user_id'] = rows.id

        return redirect('/')
    
    else:
        return render_template('login.html')

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == "__main__":
    app.debug = True
    app.run()
