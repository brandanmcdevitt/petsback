# imports for various functionality
import datetime
import random
import uuid
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth, db
from flask import Flask, redirect, render_template, request, session, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_heroku import Heroku
from flask_wtf.csrf import CsrfProtect
from helpers import login_required, upload_file
from config import KEY, ALLOWED_EXTENSIONS, FIREBASE_API, FIREBASE_AUTH_DOMAIN, FIREBASE_STORAGE_BUCKET, FIREBASE_URL, FIREBASE_JSON, SECRET_KEY
from forms import LoginForm, RegistrationForm, ReportLost, ReportFound, UpdateContactInformation
from operator import itemgetter

app = Flask(__name__)
#secret key for session
app.secret_key = KEY
app.config.from_object("config")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# #the below config links the app to a local db for local development
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/petsback'
#SESSION_COOKIE_SECURE = True
SECRET_KEY = SECRET_KEY

config = {
    "apiKey": FIREBASE_API,
    "authDomain": FIREBASE_AUTH_DOMAIN,
    "databaseURL": FIREBASE_URL,
    "storageBucket": FIREBASE_STORAGE_BUCKET,
    "serviceAccount": 'firebase.json'
}

firebase = pyrebase.initialize_app(config)

heroku = Heroku(app)
csrf = CsrfProtect(app)
csrf.init_app(app)
WTF_CSRF_ENABLED = True

# Use a service account
cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

dbf = firestore.client()

def allowed_file(filename):
    """Check if image is of the correct type"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#set homepage to index.html and personalise content
@app.route('/')
def index():
    """homepage"""

    return render_template('index.html')


# Register new users and redirect to index
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""

    user_id = session.get('user_id')
    username = session.get('username')

    #forget any previously stored user_id
    session.clear()

    form = RegistrationForm()
    form_contact = UpdateContactInformation()

    if form.validate_on_submit():
        try:
            user = auth.create_user(
                email=form.email.data,
                email_verified=False,
                password=form.password.data,
                display_name=form.username.data,
                disabled=False)
        except:
            return "Error registering user"

        #redirect the user to the homepage upon successful completion
        #return redirect('/')
        session['user_id'] = (user.uid)
        session['username'] = user.display_name
        return render_template('create-contact.html', form=form_contact)
    
    elif form_contact.validate_on_submit():
        doc_ref = dbf.collection('user_details').document(user_id)
        doc_ref.set({'forename': form_contact.forename.data,
                     'surname': form_contact.surname.data,
                     'number': form_contact.number.data,
                     'address': form_contact.address.data,
                     'city': form_contact.city.data,
                     'postcode': form_contact.postcode.data})

        session['user_id'] = user_id
        session['username'] = username

        return redirect('/')

    #else if the user reached this page via GET
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""

    #forget any previously stored user_id
    session.clear()

    form = LoginForm()

    #if user reached this page via POST and the form is validated
    if form.validate_on_submit():
        
        autho = firebase.auth()
        
        #TODO: get error codes for try catch

        try:
            user = autho.sign_in_with_email_and_password(form.username.data, form.password.data)
            # usr = auth.refresh(usr['refreshToken'])
            user_details = autho.get_account_info(user['idToken'])

            # print user['idToken']

            id_token = user['idToken']

            expires_in = datetime.timedelta(days=5)

            session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)

            # print session_cookie

            #store user_id in session
            session['user_id'] = session_cookie
            session['username'] = user_details['users'][0]['displayName']
            session['email'] = user_details['users'][0]['email']

            #request.session['uid'] = user_details['users'][0]['localId']

            #redirect to index
            return redirect('/')
        except:
            return "There was an issue logging you in"

    #else if the user reached this page via GET
    else:
        return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    """Log user out"""

    response = make_response(redirect('/'))
    response.set_cookie('session', expires=0)
    return response

    # Forget any user_id
    # session.clear()

    # Redirect user to index
    # return redirect("/")

@app.route("/account/update-info", methods=['GET', 'POST'])
@login_required
def update():
    """Update contact info"""

    user_id = session['user_id']
    doc_ref = dbf.collection('user_details').document(user_id)
    username = session['username']
    email = session['email']

    form = UpdateContactInformation()

    if form.validate_on_submit():

        if form.forename.data:
            doc_ref.update({'forename': form.forename.data})
        if form.surname.data:
            doc_ref.update({'surname': form.surname.data})
        if form.number.data is not None:
            doc_ref.update({'number': form.number.data})
        if form.address.data:
            doc_ref.update({'address': form.address.data})
        if form.city.data:
            doc_ref.update({'city': form.city.data})
        if form.postcode.data:
            doc_ref.update({'postcode': form.postcode.data})

        return redirect('/account')

    return render_template('update-info.html', username=username, email=email, form=form)

@app.route("/account")
@login_required
def account():
    """User account"""

    return render_template('account.html')

@app.route("/report")
def report():
    """Report a pet"""

    return render_template("report.html", msg="report page")

@app.route("/report/lost")
def report_lost():
    """Report Lost Pet"""

    form = ReportLost()

    if session.get("user_id") is not None:
        user_id = session['user_id']

        return render_template('report-lost.html', id=user_id, form=form)
    else:
        return render_template('report-lost.html', form=form)

@app.route("/report/found")
def report_found():
    """Report a found pet"""

    form = ReportFound()

    if session.get("user_id") is not None:
        user_id = session['user_id']

        return render_template('report-found.html', id=user_id, form=form)
    else:
        return render_template('report-found.html', form=form)

@app.route("/create-lost", methods=['GET', 'POST'])
@login_required
def create_lost():
    """Create missing report"""

    doc_ref = dbf.collection('lost').document(str(uuid.uuid4()))

    form = ReportLost()

    if form.validate_on_submit():
        # setting up the reference number to be a random generated number
        ref_no = u"PBMEL" + str(random.randint(100000, 999999))
        user_id = session['user_id']
        name = form.name.data
        age = form.age.data
        colour = form.colour.data
        sex = form.sex.data
        breed = form.breed.data
        location = form.location.data
        postcode = form.postcode.data
        animal = form.animal.data
        collar = form.collar.data
        chipped = form.chipped.data
        neutered = form.neutered.data
        #TODO: format dates to UK
        missing_since = form.missing_since.data
        post_date = datetime.datetime.now()

        #TODO: Fix image not working
        if "image" not in request.files:
            # change fallback to bool
            fallback = u"true"
        else:
            fallback = u"false"
            image = form.image.data
            image.filename = ref_no + ".jpg"
            upload_file(image, app.config["S3_BUCKET"])

        # if image and allowed_file(image.filename):

        doc_ref.set({'ref_no': ref_no, 'user_id': user_id, 'name': name,
                     'age': age, 'colour': colour, 'sex': sex, 'breed': breed,
                     'location': location, 'postcode': postcode, 'animal': animal,
                     'collar': collar, 'chipped': chipped, 'neutered': neutered,
                     'missing_since': missing_since, 'post_date': post_date,
                     'fallback': fallback})

        latest_ref = doc_ref.get().to_dict()['ref_no']

        return redirect('/posts/' + str(latest_ref))

    else:
        return render_template('report-lost.html', 
                               error_message="Please fill in the form",
                               id=session['user_id'],
                               form=form)

@app.route("/create-found", methods=['GET', 'POST'])
@login_required
def create_found():
    """Create found report"""

    doc_ref = dbf.collection('found').document(str(uuid.uuid4()))

    form = ReportFound()

    if form.validate_on_submit():
        # setting up the reference number to be a random generated number
        ref_no = u"PBMEF" + str(random.randint(100000, 999999))
        user_id = session['user_id']
        colour = form.colour.data
        sex = form.sex.data
        breed = form.breed.data
        location = form.location.data
        postcode = form.postcode.data
        animal = form.animal.data
        collar = form.collar.data
        chipped = form.chipped.data
        neutered = form.neutered.data
        #TODO: format dates to UK
        date_found = form.date_found.data
        post_date = datetime.datetime.now()

        #TODO: Fix image not working
        if "image" not in request.files:
            # change fallback to bool
            fallback = u"true"
        else:
            fallback = u"false"
            image = form.image.data
            image.filename = ref_no + ".jpg"
            upload_file(image, app.config["S3_BUCKET"])

        # if image and allowed_file(image.filename):

        doc_ref.set({'ref_no': ref_no, 'user_id': user_id, 'colour': colour,
                     'sex': sex, 'breed': breed, 'location': location,
                     'postcode': postcode, 'animal': animal,
                     'collar': collar, 'chipped': chipped, 'neutered': neutered,
                     'date_found': date_found, 'post_date': post_date, 'fallback': fallback})
        
        latest_ref = doc_ref.get().to_dict()['ref_no']

        return redirect('/posts/' + str(latest_ref))

    else:
        return render_template('report-found.html', 
                               error_message="Please fill in the form",
                               id=session['user_id'],
                               form=form)

@app.route("/posts/lost/page=<int:page>", methods=['GET'])
def posts(page=1):
    """View lost pets"""

    lost_report_ref = dbf.collection(u'lost')

    lost_report_id_list = []
    lost_posts = []
    for lost_report_id in lost_report_ref.get():
        lost_report_id_list.append(lost_report_id.id)
    for user_id in lost_report_id_list:
        try:
            doc_ref = dbf.collection(u'lost').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            lost_posts.append(latest_ref)
        except:
            pass

    ordered_by_date = sorted(lost_posts, key=itemgetter('post_date'), reverse=True)

    return render_template("posts.html", posts=ordered_by_date)

@app.route("/posts/found/page=<int:page>", methods=['GET'])
def found_posts(page=1):
    """View found pets"""

    found_report_ref = dbf.collection(u'found')

    found_report_id_list = []
    found_posts = []
    for found_report_id in found_report_ref.get():
        found_report_id_list.append(found_report_id.id)
    for user_id in found_report_id_list:
        try:
            doc_ref = dbf.collection(u'found').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            found_posts.append(latest_ref)
        except:
            pass

    ordered_by_date = sorted(found_posts, key=itemgetter('post_date'), reverse=True)

    return render_template("posts.html", posts=ordered_by_date)

@app.route("/posts/<ref>", methods=['GET'])
def post(ref):
    """Specific post page"""

    if "PBMEL" in ref:
        lost_report_ref = dbf.collection(u'lost')

        lost_report_id_list = []
        for lost_report_id in lost_report_ref.get():
            lost_report_id_list.append(lost_report_id.id)
        for user_id in lost_report_id_list:
            try:
                doc_ref = dbf.collection(u'lost').document(user_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    if value == ref:
                        return render_template('post.html', posts=latest_ref)
            except:
                pass
        return render_template('post.html', posts=latest_ref)
    elif "PBMEF" in ref:
        found_report_ref = dbf.collection(u'found')

        found_report_id_list = []
        for found_report_id in found_report_ref.get():
            found_report_id_list.append(found_report_id.id)
        for user_id in found_report_id_list:
            try:
                doc_ref = dbf.collection(u'found').document(user_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    if value == ref:
                        return render_template('post.html', posts=latest_ref)
            except:
                pass
        return render_template('post.html', posts=latest_ref)
    

@app.route("/account/my-posts/lost")
@login_required
def my_posts_lost():
    """Display user posts in my account"""

    lost_report_ref = dbf.collection(u'lost')

    lost_report_id_list = []
    lost_posts = []
    for lost_report_id in lost_report_ref.get():
        lost_report_id_list.append(lost_report_id.id)
    for user_id in lost_report_id_list:
        try:
            doc_ref = dbf.collection(u'lost').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            if latest_ref['user_id'] == session['user_id']:
                lost_posts.append(latest_ref)
        except:
            pass

    ordered_by_date = sorted(lost_posts, key=itemgetter('post_date'), reverse=True)

    return render_template("posts.html", posts=ordered_by_date, view="user")


@app.route("/account/my-posts/found")
@login_required
def my_posts_found():
    """Display user posts in my account"""

    found_report_ref = dbf.collection(u'found')

    found_report_id_list = []
    found_posts = []
    for found_report_id in found_report_ref.get():
        found_report_id_list.append(found_report_id.id)
    for user_id in found_report_id_list:
        try:
            doc_ref = dbf.collection(u'found').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            if latest_ref['user_id'] == session['user_id']:
                found_posts.append(latest_ref)
        except:
            pass

    ordered_by_date = sorted(found_posts, key=itemgetter('post_date'), reverse=True)

    return render_template("posts.html", posts=ordered_by_date, view="user")


# @app.route('/sessionLogin', methods=['POST'])
# def session_login():
#     # Get the ID token sent by the client
#     id_token = request.json['idToken']
#     # Set session expiration to 5 days.
#     expires_in = datetime.timedelta(days=5)
#     try:
#         # Create the session cookie. This will also verify the ID token in the process.
#         # The session cookie will have the same claims as the ID token.
#         session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
#         response = jsonify({'status': 'success'})
#         # Set cookie policy for session cookie.
#         expires = datetime.datetime.now() + expires_in
#         response.set_cookie(
#             'session', session_cookie, expires=expires, httponly=True, secure=True)
#         return response
#     except auth.AuthError:
#         return abort(401, 'Failed to create a session cookie')

if __name__ == "__main__":
    app.debug = True
    app.run()
