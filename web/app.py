#import secret
import os, json, boto3, datetime, random, boto
from boto.s3.connection import S3Connection
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy, Pagination
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
#importing heroku to connect with my postgres database
from flask_heroku import Heroku
from helpers import login_required, upload_file_to_s3
from config import KEY

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)
app.config.from_object("config")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
heroku = Heroku(app)
db = SQLAlchemy(app)
#import data model from models.py
from models import User, Contact, Posts

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

@app.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    """Create post"""

    if request.method == 'POST':
        refNo = "PBME" + str(random.randint(300000, 999999))
        title = request.form.get('title')
        name = request.form.get('name')
        age = request.form.get('age')
        colour = request.form.get('colour')
        gender = request.form.get('gender')
        breed = request.form.get('breed')
        status = request.form.get('status')
        location = request.form.get('location')
        postcode = request.form.get('postcode')
        animal = request.form.get('animal')
        collar = request.form.get('collar')
        chipped = request.form.get('chipped')
        neutered = request.form.get('neutered')
        missingSince = request.form.get('missingSince')
        postDate = datetime.datetime.now()


        # ******************************** TEST

        if "file" not in request.files:
            return "No file key in request.files"

	    # B
        file    = request.files["file"]

        """
        These attributes are also available

        file.filename               # The actual name of the file
        file.content_type
        file.content_length
        file.mimetype

        """

	    # C.
        if file.filename == "":
            return "Please select a file"

	    # D.
        if file and allowed_file(file.filename):
            file.filename = refNo + ".jpg"
            output   	  = upload_file_to_s3(file, app.config["S3_BUCKET"])
            
            posts = Posts(refNo, title, name, age, colour, gender, breed, status, location, postcode,
                     animal, collar, chipped, neutered, missingSince, postDate)
            db.session.add(posts)
            db.session.commit()

            latest_post = Posts.query.order_by(Posts.post_id.desc()).first()
            latest_id = latest_post.refNo

            return redirect('/posts/' + str(latest_id))

        else:
            return redirect("/")

        #******************************* TEST


        #TODO: look into amazon s3 for storage as heroku temp stores
        # file = request.files['file']
        # file.filename = refNo + ".jpg"
        # if file and allowed_file(file.filename):
        #     filename = file.filename
        #     #TODO: use S3 for uploads ****
        #     s3 = boto.connect_s3()
        #     bucket = s3.create_bucket('my_bucket')
        #     key = bucket.new_key(filename)
        #     key.set_contents_from_file(file, headers=None, replace=True, cb=None, num_cb=10, policy=None, md5=None) 
        #     return 'successful upload'
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file', filename=filename))

    

        

        #TODO: redirect user to /posts/id/title with id that has just been created
        #return render_template('post.html', post_id=latest_id)

        # use this code for testing image uploads 
        #return redirect(url_for('uploaded_file', filename=filename))

        
    
    else:
        return render_template('create-post.html')

@app.route("/posts/page/<int:page>", methods=['GET'])
def posts(page = 1):
    """View posts"""

    per_page = 10
    postTime = Posts.query.order_by(Posts.post_date.desc()).paginate(page,per_page,error_out=False)

    posts_list = []
    posts = Posts.query.all()
    for post in posts:
        posts_list.append(post)

    return render_template("posts.html", posts=posts_list, paginate=postTime)

@app.route("/posts/<ref>", methods=['GET'])
def post(ref):
    """Specific post page"""

    #TODO: make URL = posts/2/title & remove %20 from URL. replace with _
    post = Posts.query.filter(Posts.refNo == ref).first()

    return render_template('post.html', refNo=post.refNo, title=post.title, name=post.name,
                                        age=post.age, colour=post.colour, gender=post.gender,
                                        breed=post.breed, status=post.status, location=post.location,
                                        postcode=post.postcode, animal=post.animal_type, collar=post.collar,
                                        chipped=post.chipped, neutered=post.neutered, missingSince=post.missingSince)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.debug = True
    app.run()
