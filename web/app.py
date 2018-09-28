from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import create_engine

from flask_heroku import Heroku

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/management'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)
engine = create_engine(db)

# Create our database model
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120), unique=False)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<E-mail %r>' % self.email

# Set "homepage" to index.html
@app.route('/')
def index():
    #db.execute("INSERT INTO users (username, email) VALUES (bob, )")

    # insert data via insert() construct
    ins = db.insert().values(username='Hello',email='World')
    conn = engine.connect()
    conn.execute(ins)


    return render_template('index.html')

# Save e-mail to database and send to success page
@app.route('/register', methods=['POST'])
def prereg():
    email = None
    if request.method == 'POST':
        email = request.form['email']
        # Check that email does not already exist (not a great query, but works)
        if not db.session.query(User).filter(User.email == email).count():
            reg = User(email)
            db.session.add(reg)
            db.session.commit()
            return render_template('success.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    app.run()