import secret
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
#importing heroku to connect with my postgres database
from flask_heroku import Heroku

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/management'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.secret_key = secret.key

# Create our database model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hash = db.Column(db.String(80), unique=False, nullable=False)

    def __init__(self, username, email, hash):
        self.username = username
        self.email = email
        self.hash = hash


    def __repr__(self):
        return '<E-mail %r>' % self.email

# Set "homepage" to index.html
@app.route('/')
def index():
    #db.execute("INSERT INTO users (username, email) VALUES (bob, )")
    return render_template('register.html')

# Save e-mail to database and send to success page
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register user"""

    #forget any previously stored user_id
    session.clear()

    #if user reached this page via POST
    if request.method == 'POST':

        #rows = db.session.query.

        password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)

        #reg = User(':username', ':email', ':password', username=request.form.get('username'), email=request.form.get('email'), password=password)
        reg = User(request.form.get('username'), request.form.get('email'), password)

        return redirect('/')

    else:
         return render_template('register.html')



    # email = None
    # if request.method == 'POST':
    #     email = request.form['email']
    #     # Check that email does not already exist (not a great query, but works)
    #     if not db.session.query(User).filter(User.email == email).count():
    #         reg = User(email)
    #         db.session.add(reg)
    #         db.session.commit()
    #         return render_template('success.html')
    # return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run()