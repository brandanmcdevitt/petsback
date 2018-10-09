# imports for various functionality
import os, json, boto3, datetime, random, boto
from boto.s3.connection import S3Connection
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy, Pagination
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from flask_heroku import Heroku
from helpers import login_required, upload_file
from config import KEY, ALLOWED_EXTENSIONS
from forms import LoginForm

app = Flask(__name__)
app.config.from_object("config")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)
#import data model from models.py
from models import User, Contact, Lost, Found

#secret key for session
app.secret_key = KEY

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#set homepage to index.html and personalise content
@app.route('/')
def index():
    """homepage"""

    #if 'user_id' exists within the session return index.html and pass in username
    if session.get("user_id") is not None:
        user_id = session['user_id']
        rows = User.query.filter(User.id == user_id).first()
        username = rows.username

        return render_template('index.html', username=username)

    #else return index.html
    else:
        return render_template('index.html')


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
            empty_username = "No username submitted"
            return render_template('register.html', error=empty_username)
        #ensure email was submitted
        elif not request.form.get('email'):
            empty_email = "No email submitted"
            return render_template('register.html', error=empty_email)
        elif "@" not in request.form.get('email'):
            email_format = "Incorrect email format"
            return render_template('register.html', error=email_format)
        #ensure a password was submitted
        elif not request.form.get('password') or not request.form.get('confirmation'):
            empty_password = "No password submitted"
            return render_template('register.html', error=empty_password)

        #ensure that the username and email doesn't already exist in the database
        rows = User.query.all()
        for user in rows:
            if request.form.get('username').lower() == user.username.lower():
                username_exists = "Username already exists"
                return render_template('register.html', error=username_exists)
            elif request.form.get('email').lower() == user.email.lower():
                email_exists = "Email address already registered"
                return render_template('register.html', error=email_exists)

        #ensure that the passwords match
        if request.form.get('password') != request.form.get('confirmation'):
            no_match = "Passwords do not match"
            return render_template('register.html', error=no_match)
        #else hash password for security
        else:
            password = generate_password_hash(request.form.get('password'),
                                              method='pbkdf2:sha256',
                                              salt_length=8)

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
        #TODO: remove ???
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

    form = LoginForm()

    #if user reached this page via POST
    if request.method == 'POST':

        if form.validate_on_submit():
            #return either 1 or 0 if the username exists
            #TODO: fix case sensitivity
            count = User.query.filter(User.username == form.username.data).count()
            #query the database for user details
            user = User.query.filter(User.username == form.username.data).first()

            #if the count is not 1 and the password doesnt match the input, throw error
            if count != 1 or not check_password_hash(user.hash, request.form.get('password')):
                invalid_entry = "Incorrect username/password"
                return render_template('login.html', error=invalid_entry)

            session['user_id'] = user.id

            return redirect('/')

        return render_template('login.html', form=form)

        # *******************

        # #ensure that a username was submitted
        # if not request.form.get('username'):
        #     empty_username = "No username submitted"
        #     return render_template('login.html', error=empty_username)

        # #ensure the password was submitted
        # elif not request.form.get('password'):
        #     empty_password = "No password submitted"
        #     return render_template('login.html', error=empty_password)

        # #return either 1 or 0 if the username exists
        # #TODO: fix case sensitivity
        # count = User.query.filter(User.username == request.form.get('username')).count()
        # #query the database for user details
        # user = User.query.filter(User.username == request.form.get('username')).first()

        # #if the count is not 1 and the password doesnt match the input, throw error
        # if count != 1 or not check_password_hash(user.hash, request.form.get('password')):
        #     invalid_entry = "Incorrect username/password"
        #     return render_template('login.html', error=invalid_entry)

        # session['user_id'] = user.id

        # return redirect('/')

        # *********************
    
    #else if the user reached this page via GET
    else:
        return render_template('login.html', form=form)

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

    #TODO: remove if statement?
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

@app.route("/report")
def report():
    """Report a pet"""

    return render_template("report.html")

@app.route("/report/lost")
def report_lost():
    """Report Lost Pet"""

    if session.get("user_id") is not None:
        user_id = session['user_id']

        return render_template('report-lost.html', id=user_id)
    else:
        return render_template('report-lost.html')

@app.route("/report/found")
def report_found():
    """Report a found pet"""

    if session.get("user_id") is not None:
        user_id = session['user_id']

        return render_template('report-found.html', id=user_id)
    else:
        return render_template('report-found.html')

@app.route("/create-lost", methods=['GET', 'POST'])
@login_required
def create_lost():
    """Create missing report"""

    if request.method == 'POST':
        # setting up the reference number to be a random generated number
        ref_no = "PBME" + str(random.randint(100000, 999999))
        user_id = session['user_id']
        name = request.form.get('name')
        age = request.form.get('age')
        colour = request.form.get('colour')
        sex = request.form.get('sex')
        breed = request.form.get('breed')
        location = request.form.get('location')
        postcode = request.form.get('postcode')
        animal = request.form.get('animal')
        collar = request.form.get('collar')
        chipped = request.form.get('chipped')
        neutered = request.form.get('neutered')
        #TODO: format dates to UK
        missing_since = request.form.get('missing_since')
        post_date = datetime.datetime.now()

        if "file" not in request.files:
            return "No file key in request.files"

        file = request.files["file"]

        if file.filename == "":
            return "Please select a file"

        if file and allowed_file(file.filename):
            file.filename = ref_no + ".jpg"
            upload_file(file, app.config["S3_BUCKET"])

            reports = Lost(ref_no, user_id, name, age, colour, sex, breed, location, postcode,
                           animal, collar, chipped, neutered, missing_since, post_date)
            db.session.add(reports)
            db.session.commit()

            latest_report = Lost.query.order_by(Lost.post_id.desc()).first()
            latest_ref = latest_report.ref_no

            return redirect('/posts/' + str(latest_ref))

        else:
            return redirect("/")
    
    else:
        return render_template('report.html')

@app.route("/create-found", methods=['GET', 'POST'])
@login_required
def create_found():
    """Create found report"""

@app.route("/posts/page=<int:page>", methods=['GET'])
def posts(page = 1):
    """View posts"""

    per_page = 10
    reports = Lost.query.order_by(Lost.post_date.desc()).paginate(page,per_page,error_out=False)

    return render_template("posts.html", posts=reports)

@app.route("/posts/<ref>", methods=['GET'])
def post(ref):
    """Specific post page"""

    post = Lost.query.filter(Lost.ref_no == ref).first()

    return render_template('post.html',
                           ref_no=post.ref_no,
                           name=post.name,
                           age=post.age,
                           colour=post.colour,
                           sex=post.sex,
                           breed=post.breed,
                           location=post.location,
                           postcode=post.postcode,
                           animal=post.animal_type,
                           collar=post.collar,
                           chipped=post.chipped,
                           neutered=post.neutered,
                           missing_since=post.missing_since)


@app.route("/account/my-posts")
@login_required
def my_posts():
    """Display user posts in my account"""

    user_id = session['user_id']
    count = Lost.query.filter(Lost.user_id == user_id).order_by(Lost.post_date.desc()).count()

    if count != 0:
        posts = Lost.query.filter(Lost.user_id == user_id).order_by(Lost.post_date.desc())
        return render_template('user-posts.html', posts=posts)
    else:
        return render_template('user-posts.html')

@app.route('/test')
def test():
    """logiin"""
    form = LoginForm()
    return render_template('test.html', title='Sign In', form=form)

if __name__ == "__main__":
    app.debug = True
    app.run()
