# imports for various functionality
import datetime
import random
import uuid
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore, auth, db
from flask import Flask, redirect, render_template, request, session, make_response, jsonify, abort, flash
from werkzeug.utils import secure_filename
from flask_heroku import Heroku
from flask_wtf.csrf import CSRFProtect
from helpers import login_required, upload_file, upload_qr
from config import KEY, PYREBASE_CONFIG
from forms import *
from operator import itemgetter
import qrcode
import sys, os, io
from PIL import Image
from tf_model import model

from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from helpers import allowed_file

app = Flask(__name__)
#secret key for session
app.secret_key = KEY
app.config.from_object("config")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

heroku = Heroku(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
#WTF_CSRF_ENABLED = True

# setting up firebase, pyrebase and firestore for data storage
#TODO: research how to hide json file for credentials
cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(PYREBASE_CONFIG)
dbf = firestore.client()

#set homepage to index.html
@app.route('/')
def index():
    """
    homepage
    """

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration
    """

    # declare and set user_id, username and email from the sesssion before clearing
    user_id = session.get('user_id')
    username = session.get('username')
    email = session.get('email')

    #forget any previously stored session variable
    session.clear()

    # initialise the registration and update contact form objects
    form = RegistrationForm()
    form_contact = UpdateContactInformation()

    # if the forms inputs are validated and the user has returned via POST
    if form.validate_on_submit():
        # try to create a new user through firebase with an email and password
        try:
            #TODO: check the validation on firebase for user registration
            user = auth.create_user(
                email=form.email.data,
                email_verified=False,
                password=form.password.data,
                display_name=form.username.data,
                disabled=False)
        #TODO: find proper google exception error messages for this
        except:
            return "Error registering user"

        # set the session variables to the users unique ID and username
        session['user_id'] = (user.uid)
        session['username'] = user.display_name
        session['email'] = user.email
        # render the template for filling in contact information and pass in the contact form
        return render_template('create-contact.html', form=form_contact)
    
    # if the contact form has been submitted and validated then set the user_details collection info
    elif form_contact.validate_on_submit():
        # getting a reference to the firebase collection with the user_id as a unique identifier
        doc_ref = dbf.collection('user_details').document(user_id)
        # push the data taken from the forms into the document in firebase
        doc_ref.set({'forename': form_contact.forename.data,
                     'surname': form_contact.surname.data,
                     'number': form_contact.number.data,
                     'address': form_contact.address.data,
                     'city': form_contact.city.data,
                     'postcode': form_contact.postcode.data})

        # re-setting the session variables as they had been cleared upon entering the registration page
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email

        #re-direct the user to the homepage upon successful completion
        return redirect('/')

    #else if the user reached this page via GET
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login
    """

    # clear the session
    session.clear()
    
    # get the login form object
    form = LoginForm()

    # if the form has validated and the user has came by POST
    if form.validate_on_submit():
        firebase_auth = firebase.auth()

        # try to log the user in and create a session
        try:
            # creating the user if log in was successful
            user = firebase_auth.sign_in_with_email_and_password(form.username.data, form.password.data)
            # user details will hold all of the information returned by the idToken
            id_token = user['idToken']
            user_details = firebase_auth.get_account_info(id_token)

            # Set session expiration to 5 days.
            expires_in = datetime.timedelta(days=5)
            try:
                # Create the session cookie. This will also verify the ID token in the process.
                # The session cookie will have the same claims as the ID token.
                session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
                session['user_id'] = user_details['users'][0]['localId']
                session['username'] = user_details['users'][0]['displayName']
                session['email'] = user_details['users'][0]['email']
                response = jsonify({'status': 'success'})
                # Set cookie policy for session cookie.
                expires = datetime.datetime.now() + expires_in
                response.set_cookie(
                    'session', session_cookie, expires=expires, httponly=True, secure=True)
                return redirect('/')
            except auth.AuthError:
                return abort(401, 'Failed to create a session cookie')
        #TODO: get proper exception error message from google firebase
        except:
            return "error logging in"

    #else if the user reached this page via GET
    else:
        return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    """
    Log user out
    """

    response = make_response(redirect('/'))
    response.set_cookie('session', expires=0)
    #return response
    #Forget any user_id
    session.clear()
    #Redirect user to index
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():
    """
    User dashboard
    """

    count = 0

   # create a reference to the found documents
    reg_pet_ref = dbf.collection(u'reg_pet')
    # create a list for the IDs and posts
    reg_pet_id_list = []
    for reg_pet_id in reg_pet_ref.get():
        reg_pet_id_list.append(reg_pet_id.id)
    for user_id in reg_pet_id_list:
        try:
            doc_ref = dbf.collection(u'reg_pet').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            # if the user_id is equal to the id of the logged in user then add this post to the list
            if latest_ref['user_id'] == session['user_id']:
                count += 1
        except:
            pass

    return render_template('dashboard.html', count=count)

@app.route("/register-a-pet", methods=["GET", "POST"])
def register_a_pet_pre():
    """
    Pet registration
    """

    form = ResgisterPet()

    doc_ref = dbf.collection('reg_pet').document(str(uuid.uuid4()))

    if form.validate_on_submit():
        ref_no = u"PBMER" + str(random.randint(100000, 999999))
        user_id = session['user_id']
        # if no image has been submitted then display a fallback image
        if "image" not in request.files:
            # change fallback to bool
            fallback = u"true"
        # else pass the image file into the upload_file() function in helpers.py
        else:
            fallback = u"false"
            image = form.image.data
            image.filename = ref_no + ".jpg"
            upload_file(image, app.config["S3_BUCKET"])

        #TODO: re-add image validation
        # if image and allowed_file(image.filename):

        # generate and save QR code
        qr = qrcode.QRCode(version=1,
                           error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=10,
                           border=4,)
        qr.add_data("http://petsback.me/pet/{}".format(ref_no))
        qr.make(fit=True)
        img = qr.make_image()
        img.save("../tmp/qr-{}.png".format(ref_no))
        
        script_dir = sys.path[0]
        img_path = os.path.join(script_dir, 'tmp/qr-{}.png'.format(ref_no))

        image_name = "qr-{}.png".format(ref_no)
        # upload QR to amazon s3 bucket
        upload_qr('/tmp/qr-{}.png'.format(ref_no), image_name)

        doc_ref.set({'ref_no': ref_no,
                     'name': form.name.data,
                     'colour': form.colour.data,
                     'sex': form.sex.data,
                     'breed': form.breed.data,
                     'location': form.location.data,
                     'postcode': form.postcode.data,
                     'animal': form.animal.data,
                     'fallback': fallback,
                     'user_id': user_id})

        return redirect('/pet/' + str(ref_no))

    return render_template('register-pet.html', form=form)

@app.route("/pet/<ref>")
def view_registered_pet(ref):

    # create a reference to the lost documents
    reg_pet_ref = dbf.collection(u'reg_pet')
    # create a list for the IDs
    reg_pet_id_list = []
    for reg_pet_id in reg_pet_ref.get():
        reg_pet_id_list.append(reg_pet_id.id)
    for user_id in reg_pet_id_list:
        try:
            doc_ref = dbf.collection(u'reg_pet').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            for key, value in latest_ref.items():
                #if the value is equal to ref then render the page with the latest value being passed in
                if value == ref:
                    return render_template('pet.html', posts=latest_ref)
        #TODO: get proper exception error handling from google firebase
        except:
            pass
    return render_template('post.html', posts=latest_ref)

    return "We could not find your post"


@app.route("/account/update-info", methods=['GET', 'POST'])
@login_required
def update():
    """
    Update contact info
    """

    # declaring variables from session and creating a reference to the firebase document
    user_id = session['user_id']
    username = session['username']
    email = session['email']
    doc_ref = dbf.collection('user_details').document(user_id)

    # creating the update contact information form
    form = UpdateContactInformation()

    # if form has been validated and user has came by POST
    if form.validate_on_submit():
        # only push new data to the firebase document instead of wiping data with blank fields
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
    # else if the user has arrived by GET
    return render_template('update-info.html', username=username, email=email, form=form)

@app.route("/account")
@login_required
def account():
    """
    User account dashboard
    """

    return render_template('account.html')

@app.route("/report")
def report():
    """
    Report a pet
    """

    return render_template("report.html", msg="report page")

@app.route("/report/lost")
def report_lost():
    """
    Report Lost Pet
    """
    # create the report lost object
    form = ReportLost()
    # if the session variable exists then display the form with fields, 
    # else if none exists ask the user to register or log in
    if session.get("user_id") is not None:
        user_id = session['user_id']
        
        return render_template('report-lost.html', id=user_id, form=form)
    else:
        return render_template('report-lost.html', form=form)

@app.route("/report/found")
def report_found():
    """
    Report a found pet
    """
    # create the report found object
    form = ReportFound()

    # if the session variable exists then display the form with fields, 
    # else if none exists ask the user to register or log in
    if session.get("user_id") is not None:
        user_id = session['user_id']

        return render_template('report-found.html', id=user_id, form=form)
    else:
        return render_template('report-found.html', form=form)

@app.route("/create-lost", methods=['GET', 'POST'])
@login_required
def create_lost():
    """
    Create missing report
    """
    # set the reference to the document on firebase in the lost collection
    # the document will have a unique id generated by uuid
    doc_ref = dbf.collection('lost').document(str(uuid.uuid4()))

    # create the lost report object
    form = ReportLost()

    # if the form has been validated and the user has arrived via POST
    if form.validate_on_submit():
        # declaring variables from the form data
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
        missing_since = form.missing_since.data
        post_date = datetime.datetime.now()
        email = session['email']

        # if no image has been submitted then display a fallback image
        if "image" not in request.files:
            # change fallback to bool
            fallback = u"true"
        # else pass the image file into the upload_file() function in helpers.py
        else:
            fallback = u"false"
            image = form.image.data
            image.filename = ref_no + ".jpg"
            upload_file(image, app.config["S3_BUCKET"])

        #TODO: re-add image validation
        # if image and allowed_file(image.filename):

        # commit the data to the document in firebase
        doc_ref.set({'ref_no': ref_no, 'user_id': user_id, 'name': name,
                     'age': age, 'colour': colour, 'sex': sex, 'breed': breed,
                     'location': location, 'postcode': postcode, 'animal': animal,
                     'collar': collar, 'chipped': chipped, 'neutered': neutered,
                     'missing_since': missing_since, 'post_date': post_date,
                     'fallback': fallback, 'email': email})

        # latest_ref = doc_ref.get().to_dict()['ref_no']

        # return the post page that had just been created
        return redirect('/posts/' + str(ref_no))

    # else if the user arrived by GET
    return render_template('report-lost.html',
                           error_message="Please fill in the form",
                           id=session['user_id'],
                           form=form)

@app.route("/create-found", methods=['GET', 'POST'])
@login_required
def create_found():
    """
    Create found report
    """
    # set the reference to the document on firebase in the found collection
    # the document will have a unique id generated by uuid
    doc_ref = dbf.collection('found').document(str(uuid.uuid4()))

    # create the found report object
    form = ReportFound()

    # if the form has been validated and the user has arrived via POST
    if form.validate_on_submit():
        # declaring variables from the form data
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
        email = session['email']

        # if no image has been submitted then display a fallback image
        if "image" not in request.files:
            # change fallback to bool
            fallback = u"true"
        # else pass the image file into the upload_file() function in helpers.py
        else:
            fallback = u"false"
            image = form.image.data
            image.filename = ref_no + ".jpg"
            upload_file(image, app.config["S3_BUCKET"])

        #TODO: re-add image validation
        # if image and allowed_file(image.filename):

       # commit the data to the document in firebase 
        doc_ref.set({'ref_no': ref_no, 'user_id': user_id, 'colour': colour,
                     'sex': sex, 'breed': breed, 'location': location,
                     'postcode': postcode, 'animal': animal,
                     'collar': collar, 'chipped': chipped, 'neutered': neutered,
                     'date_found': date_found, 'post_date': post_date, 'fallback': fallback,
                     'email': email})
        
        #latest_ref = doc_ref.get().to_dict()['ref_no']

        # return the post page that had just been created
        return redirect('/posts/' + str(ref_no))
    # else if the user arrived by GET
    return render_template('report-found.html', 
                           error_message="Please fill in the form",
                           id=session['user_id'],
                           form=form)

@app.route("/posts/lost/page=<int:page>", methods=['GET'])
def posts(page=1):
    """
    View lost pets
    """
    # creating a reference to the lost collection on firebase
    lost_report_ref = dbf.collection(u'lost')
    # create a list to hold the post IDs and another to hold the posts
    lost_report_id_list = []
    lost_posts = []
    # for the ID in the lost report reference add the IDs to the list
    for lost_report_id in lost_report_ref.get():
        lost_report_id_list.append(lost_report_id.id)
    # for the user ID in the list of IDs
    for user_id in lost_report_id_list:
        try:
            doc_ref = dbf.collection(u'lost').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            lost_posts.append(latest_ref)
        #TODO: get proper exception error handling from google firebase
        except:
            pass
    # order the list by the post_date in descending order
    ordered_by_date = sorted(lost_posts, key=itemgetter('post_date'), reverse=True)
    # return the posts template and pass in the ordered posts
    return render_template("posts.html", posts=ordered_by_date)

@app.route("/posts/found/page=<int:page>", methods=['GET'])
def posts_found(page=1):
    """
    View found pets
    """
    # creating a reference to the found collection on firebase
    found_report_ref = dbf.collection(u'found')
    # create a list to hold the post IDs and another to hold the posts
    found_report_id_list = []
    found_posts = []
    # for the ID in the lost report reference add the IDs to the list
    for found_report_id in found_report_ref.get():
        found_report_id_list.append(found_report_id.id)
    # for the user ID in the list of IDs
    for user_id in found_report_id_list:
        try:
            doc_ref = dbf.collection(u'found').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            found_posts.append(latest_ref)
        #TODO: get proper exception error handling from google firebase
        except:
            pass
    # order the list by the post_date in descending order
    ordered_by_date = sorted(found_posts, key=itemgetter('post_date'), reverse=True)
    # return the posts template and pass in the ordered posts
    return render_template("posts.html", posts=ordered_by_date)

@app.route("/posts/<ref>", methods=['GET'])
def post(ref):
    """
    Specific post page
    """

    # if ref contains "PBMEL" (L = lost) then run this block of code
    if "PBMEL" in ref:
        # create a reference to the lost documents
        lost_report_ref = dbf.collection(u'lost')
        # create a list for the IDs
        lost_report_id_list = []
        for lost_report_id in lost_report_ref.get():
            lost_report_id_list.append(lost_report_id.id)
        for user_id in lost_report_id_list:
            try:
                doc_ref = dbf.collection(u'lost').document(user_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        return render_template('post.html', posts=latest_ref, user_id=session['user_id'])
            #TODO: get proper exception error handling from google firebase
            except:
                pass
        return render_template('post.html', posts=latest_ref)
    #else if ref contains "PBMEF" (F = found) then run this block of code.
    elif "PBMEF" in ref:
        # create a reference to the found documents
        found_report_ref = dbf.collection(u'found')
        # create a list for the IDs
        found_report_id_list = []
        for found_report_id in found_report_ref.get():
            found_report_id_list.append(found_report_id.id)
        for user_id in found_report_id_list:
            try:
                doc_ref = dbf.collection(u'found').document(user_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        return render_template('post.html', posts=latest_ref, user_id=session['user_id'])
            #TODO: get proper exception error handling from google firebase
            except:
                pass
    # else return error
    else:
        return "We could not find your post"


@app.route("/delete-post", methods=["POST"])
@login_required
def delete_post():

    ref = request.form['info']

    if "PBMEL" in ref:
        # create a reference to the lost documents
        delete_ref = dbf.collection(u'lost')
        # create a list for the IDs
        delete_id_list = []
        for delete_id in delete_ref.get():
            delete_id_list.append(delete_id.id)
        for doc_id in delete_id_list:
            try:
                doc_ref = dbf.collection(u'lost').document(doc_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        # delete the document
                        dbf.collection(u'lost').document(doc_id).delete()
                        return redirect('/posts/lost/page=1')
            #TODO: get proper exception error handling from google firebase
            except:
                pass
        return render_template('post.html', posts=latest_ref)
    #else if ref contains "PBMEF" (F = found) then run this block of code.
    elif "PBMEF" in ref:
        # create a reference to the found documents
        found_report_ref = dbf.collection(u'found')
        # create a list for the IDs
        found_report_id_list = []
        for found_report_id in found_report_ref.get():
            found_report_id_list.append(found_report_id.id)
        for user_id in found_report_id_list:
            try:
                doc_ref = dbf.collection(u'found').document(user_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        # delete the document
                        dbf.collection(u'found').document(user_id).delete()
                        return redirect('/posts/lost/page=1')
            #TODO: get proper exception error handling from google firebase
            except:
                pass
    # else return error
    else:
        return "We could not find your post"
    

@app.route('/edit-post', methods=["POST"])
@login_required
def edit_post():
    ref = request.form['info']
    form = ReportLost()

    if "PBMEL" in ref:
        # create a reference to the lost documents
        edit_ref = dbf.collection(u'lost')
        # create a list for the IDs
        edit_id_list = []
        for edit_id in edit_ref.get():
            edit_id_list.append(edit_id.id)
        for doc_id in edit_id_list:
            try:
                doc_ref = dbf.collection(u'lost').document(doc_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        return render_template('report-lost.html', posts=latest_ref, form=form,
                                                id=session['user_id'], edit="true")
            #TODO: get proper exception error handling from google firebase
            except:
                pass
        return render_template('report-lost.html', posts=latest_ref, form=form,
                                id=session['user_id'], edit="true")
    #else if ref contains "PBMEF" (F = found) then run this block of code.
    elif "PBMEF" in ref:
        # create a reference to the found documents
        found_report_ref = dbf.collection(u'found')
        # create a list for the IDs
        found_report_id_list = []
        for found_report_id in found_report_ref.get():
            found_report_id_list.append(found_report_id.id)
        for user_id in found_report_id_list:
            try:
                doc_ref = dbf.collection(u'found').document(user_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        return render_template('report-found.html', posts=latest_ref, form=form,
                                                id=session['user_id'], edit="true")
            #TODO: get proper exception error handling from google firebase
            except:
                pass
    # else return error
    else:
        return "We could not find your post"

@app.route("/submit-edit", methods=['GET', 'POST'])
@login_required
def submit_edit():
    """
    Update pet report
    """

    ref = request.form['info']

    if "PBMEL" in ref:
        form = ReportLost()
        # create a reference to the lost documents
        edit_ref = dbf.collection(u'lost')
        # create a list for the IDs
        edit_id_list = []
        for edit_id in edit_ref.get():
            edit_id_list.append(edit_id.id)
        for doc_id in edit_id_list:
            try:
                doc_ref = dbf.collection(u'lost').document(doc_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        # update the report
                        doc_ref.update({'name': form.name.data,
                                        'age': form.age.data,
                                        'colour': form.colour.data,
                                        'breed': form.breed.data,
                                        'location': form.location.data,
                                        'postcode': form.postcode.data})
                        return redirect('posts/{}'.format(ref))
            #TODO: get proper exception error handling from google firebase
            except:
                pass
        return redirect('posts/{}'.format(ref))
    #else if ref contains "PBMEF" (F = found) then run this block of code.
    elif "PBMEF" in ref:
        form = ReportFound()
        # create a reference to the found documents
        found_report_ref = dbf.collection(u'found')
        # create a list for the IDs
        found_report_id_list = []
        for found_report_id in found_report_ref.get():
            found_report_id_list.append(found_report_id.id)
        for user_id in found_report_id_list:
            try:
                doc_ref = dbf.collection(u'found').document(user_id)
                latest_ref = doc_ref.get().to_dict()
                for key, value in latest_ref.items():
                    #if the value is equal to ref then render the page with the latest value being passed in
                    if value == ref:
                        # update the report
                        doc_ref.update({'colour': form.colour.data,
                                        'breed': form.breed.data,
                                        'location': form.location.data,
                                        'postcode': form.postcode.data})
                        return redirect('posts/{}'.format(ref))
            #TODO: get proper exception error handling from google firebase
            except:
                pass
    # else return error
    else:
        return "We could not find your post"
    


@app.route("/account/my-posts/lost")
@login_required
def my_posts_lost():
    """
    Display user posts in my account
    """
    # create a reference to the lost documents
    lost_report_ref = dbf.collection(u'lost')
    # create a list for the IDs and posts
    lost_report_id_list = []
    lost_posts = []
    for lost_report_id in lost_report_ref.get():
        lost_report_id_list.append(lost_report_id.id)
    for user_id in lost_report_id_list:
        try:
            doc_ref = dbf.collection(u'lost').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            # if the user_id is equal to the id of the logged in user then add this post to the list
            if latest_ref['user_id'] == session['user_id']:
                lost_posts.append(latest_ref)
        except:
            pass
    # order the list by the post_date in descending order
    ordered_by_date = sorted(lost_posts, key=itemgetter('post_date'), reverse=True)
    # pass the ordered list into the posts page with the user string
    return render_template("posts.html", posts=ordered_by_date, view="user")


@app.route("/account/my-posts/found")
@login_required
def my_posts_found():
    """
    Display user posts in my account
    """
    # create a reference to the found documents
    found_report_ref = dbf.collection(u'found')
    # create a list for the IDs and posts
    found_report_id_list = []
    found_posts = []
    for found_report_id in found_report_ref.get():
        found_report_id_list.append(found_report_id.id)
    for user_id in found_report_id_list:
        try:
            doc_ref = dbf.collection(u'found').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            # if the user_id is equal to the id of the logged in user then add this post to the list
            if latest_ref['user_id'] == session['user_id']:
                found_posts.append(latest_ref)
        except:
            pass
    # order the list by the post_date in descending order
    ordered_by_date = sorted(found_posts, key=itemgetter('post_date'), reverse=True)
    # pass the ordered list into the posts page with the user string
    return render_template("posts.html", posts=ordered_by_date, view="user")


@app.route("/account/my-pets")
@login_required
def my_pets():
    """
    """
    # create a reference to the found documents
    reg_pet_ref = dbf.collection(u'reg_pet')
    # create a list for the IDs and posts
    reg_pet_id_list = []
    reg_pet_posts = []
    for reg_pet_id in reg_pet_ref.get():
        reg_pet_id_list.append(reg_pet_id.id)
    for user_id in reg_pet_id_list:
        try:
            doc_ref = dbf.collection(u'reg_pet').document(user_id)
            latest_ref = doc_ref.get().to_dict()
            # if the user_id is equal to the id of the logged in user then add this post to the list
            if latest_ref['user_id'] == session['user_id']:
                reg_pet_posts.append(latest_ref)
        except:
            pass
    # order the list by the post_date in descending order
    #ordered_by_date = sorted(reg_pet_posts, key=itemgetter('post_date'), reverse=True)
    # pass the ordered list into the posts page with the user string
    return render_template("my-pets.html", posts=reg_pet_posts)

@app.route('/tf_breed', methods=["POST"])
def return_breed():
    """
    """
    if request.method == 'POST':
    # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            file_name = 'tmp/{}'.format(filename)

            user_id = session['user_id']

            form = ReportLost()

            return model.classify(file_name, user_id, form)


if __name__ == "__main__":
    app.debug = True
    app.run()
