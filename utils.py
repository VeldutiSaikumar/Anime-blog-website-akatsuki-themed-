from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_mail import Message
from .extensions import mail
from cloudinary.uploader import upload as cloud_upload
from werkzeug.utils import secure_filename

def generate_token(email, salt='email-confirm'):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt=salt)

def confirm_token(token, salt='email-confirm', expiration=None):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    max_age = expiration or current_app.config.get('EMAIL_TOKEN_EXPIRATION', 3600)
    return s.loads(token, salt=salt, max_age=max_age)

def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients, html=html_body)
    mail.send(msg)

def upload_image(file_storage, folder='naruto_blog'):
    # file_storage is Werkzeug FileStorage
    filename = secure_filename(file_storage.filename)
    # Cloudinary will handle storage; we pass file object
    res = cloud_upload(file_storage, folder=folder)
    return res.get('secure_url')
