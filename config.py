from os import environ

DATABASE_NAME = environ['DATABASE_NAME']
DATABASE_HOST = environ['DATABASE_HOST']
DATABASE_PASSWORD = environ['DATABASE_PASSWORD']
DATABASE_USER = environ['DATABASE_USER']

CSRF_ENABLED = True
THREADS_PER_PAGE = 2

SECRET_KEY = environ['SECRET']
CSRF_SESSION_KEY = environ['CSRF_SESSION_KEY']
SECURITY_PASSWORD_SALT = environ['SECURITY_PASSWORD_SALT']

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": environ['EMAIL_USER'],
    "MAIL_PASSWORD": environ['TourKrop1337']
}
