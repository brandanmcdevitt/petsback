from functools import wraps
from flask import redirect, session
import boto3
from config import S3_KEY, S3_SECRET, S3_LOCATION, ALLOWED_EXTENSIONS, S3_BUCKET

def login_required(f):
    """
    Function for checking if a user is logged in to access certain pages.
    If they are not, then re-direct to the login page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """
    Check if image is of the correct type
    """
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

s3 = boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

def upload_file(file, bucket_name, acl="public-read"):

    """
    Function to upload images to Amazon S3 buckets.
    """

    try:

        s3.upload_fileobj(file, bucket_name, file.filename, ExtraArgs={"ACL": acl,
                                                                       "ContentType": file.content_type})

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(S3_LOCATION, file.filename)


def upload_qr(location, filename, acl="public-read"):

    s3 = boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

    bucket = S3_BUCKET

    s3.upload_file(location, bucket, filename, ExtraArgs={"ACL": acl,
                                                          "ContentType": 'image/png'})