# imports for various functionality
import datetime
import random
import uuid
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth, db
from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_heroku import Heroku
from flask_wtf.csrf import CSRFProtect
from helpers import login_required, upload_file
from config import KEY, ALLOWED_EXTENSIONS, FIREBASE_API, FIREBASE_AUTH_DOMAIN, FIREBASE_STORAGE_BUCKET, FIREBASE_URL
from forms import LoginForm, RegistrationForm, ReportLost, ReportFound, UpdateContactInformation

app = Flask(__name__)
#secret key for session
app.secret_key = KEY
app.config.from_object("config")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#the below config links the app to a local db for local development
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/petsback'

config = {
    "apiKey": FIREBASE_API,
    "authDomain": FIREBASE_AUTH_DOMAIN,
    "databaseURL": FIREBASE_URL,
    "storageBucket": FIREBASE_STORAGE_BUCKET,
    "serviceAccount": "firebase.json"
}

firebase = pyrebase.initialize_app(config)

heroku = Heroku(app)
# db = SQLAlchemy(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
#import data model from models.py
#from models import User, Contact, Lost, Found

# Use a service account
cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

dbf = firestore.client()
dbp = firebase.database()

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

        auth = firebase.auth()

        #TODO: get error codes for try catch

        user = auth.sign_in_with_email_and_password(form.username.data, form.password.data)
        # usr = auth.refresh(usr['refreshToken'])

        user_details = auth.get_account_info(user['idToken'])

        #store user_id in session
        session['user_id'] = user_details['users'][0]['localId']
        session['username'] = user_details['users'][0]['displayName']
        session['email'] = user_details['users'][0]['email']

        #redirect to index
        return redirect('/')

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
        ref_no = u"PBME" + str(random.randint(100000, 999999))
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
        ref_no = u"PBME" + str(random.randint(100000, 999999))
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

    view_all = dbp.child("lost").get()

    # per_page = 10
    # reports = Lost.query.order_by(Lost.post_date.desc()).paginate(page,
    #                                                               per_page,
    #                                                               error_out=False)

    lost_ref = dbf.collection(u'lost')
    first_query = lost_ref.order_by(u'post_date').limit(3)

    # Get the last document from the results
    docs = first_query.get()
    last_doc = list(docs)[-1]

    last_pop = last_doc.to_dict()[u'post_date']

    next_query = (
        lost_ref
        .order_by(u'post_date')
        .start_after({
            u'post_date': last_pop
        })
        .limit(3)
    )

    return render_template("posts.html", pag=next_query)

@app.route("/posts/found/page=<int:page>", methods=['GET'])
def found_posts(page=1):
    """View found pets"""

    per_page = 10
    # reports = Found.query.order_by(Found.post_date.desc()).paginate(page, per_page, error_out=False)

    return render_template("posts.html")

@app.route("/posts/<ref>", methods=['GET'])
def post(ref):
    """Specific post page"""

    ref = db.reference('lost')
    snapshot = ref.order_by_child('ref_no').limit_to_last(2).get()
    # for key in snapshot:
    #     print(key)

    lost_ref = dbf.collection(u'lost').where(u'ref_no', u'==', ref).get()
   #print lost_ref.get().to_dict()['ref_no']

    # lost = Lost.query.filter(Lost.ref_no == ref).first()
    # found = Found.query.filter(Found.ref_no == ref).first()

    # if lost:
    #     return render_template('post.html',
    #                            ref_no=lost.ref_no,
    #                            name=lost.name,
    #                            age=lost.age,
    #                            colour=lost.colour,
    #                            sex=lost.sex,
    #                            breed=lost.breed,
    #                            location=lost.location,
    #                            postcode=lost.postcode,
    #                            animal=lost.animal_type,
    #                            collar=lost.collar,
    #                            chipped=lost.chipped,
    #                            neutered=lost.neutered,
    #                            missing_since=lost.missing_since,
    #                            fallback=lost.fallback)
    # elif found:
    #     return render_template('post.html',
    #                            ref_no=found.ref_no,
    #                            colour=found.colour,
    #                            sex=found.sex,
    #                            breed=found.breed,
    #                            location=found.location,
    #                            postcode=found.postcode,
    #                            animal=found.animal_type,
    #                            collar=found.collar,
    #                            chipped=found.chipped,
    #                            neutered=found.neutered,
    #                            date_found=found.date_found,
    #                            fallback=found.fallback)


@app.route("/account/my-posts")
@login_required
def my_posts():
    """Display user posts in my account"""

    # user_id = session['user_id']
    # count = Lost.query.filter(Lost.user_id == user_id).order_by(Lost.post_date.desc()).count()

    # if count != 0:
    #     posts = Lost.query.filter(Lost.user_id == user_id).order_by(Lost.post_date.desc())
    #     return render_template('user-posts.html', posts=posts)
    # else:
    #     return render_template('user-posts.html')


if __name__ == "__main__":
    app.debug = True
    app.run()
