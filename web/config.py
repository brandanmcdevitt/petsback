import os

# credentials for amazon s3, saved as environmental variables to protect secure keys
S3_BUCKET                 = os.environ.get("S3_BUCKET_NAME")
S3_KEY                    = os.environ.get("S3_ACCESS_KEY")
S3_SECRET                 = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY                = os.urandom(32)
DEBUG                     = True
PORT                      = 5000

# secret key that persists session data
KEY = os.environ.get('SECRET_KEY')

# extensions that are allowed to be accepted in the file uplaoder
ALLOWED_EXTENSIONS = set(['jpg'])