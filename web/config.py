import os

# credentials for amazon s3, saved as environmental variables to protect secure keys
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

DEBUG = True
PORT = 5000

# secret key that persists session data
KEY = os.environ.get('SECRET_KEY')

# extensions that are allowed to be accepted in the file uplaoder
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOAD_FOLDER = 'tmp'

# pyrebase config
PYREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_API"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.environ.get("FIREBASE_URL"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "serviceAccount": 'firebase.json'
}

MODEL_FILE = "tf_model/tf_files/models/retrained_graph.pb.icloud"
LABEL_FILE = "tf_model/tf_files/models/retrained_labels.txt"
INPUT_HEIGHT = 224
INPUT_WIDTH = 224
INPUT_MEAN = 128
INPUT_STD = 128
INPUT_LAYER = "input"
OUTPUT_LAYER = "final_result"