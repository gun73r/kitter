from functools import wraps
from flask import redirect, url_for, session, Response

from app.models import *


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session['logged_in']:
            return Response({'message': 'Unauthorised'})
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session['logged_in'] or not get_current_user().is_admin:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return wrapper


def my_converter(inst):
    if isinstance(inst, datetime.datetime):
        return inst.__str__()



def get_current_user():
    if session.get('logged_in'):
        try:
            return User.get(User.id == session.get('user_id'))
        except User.DoesNotExist:
            logout_user()


def auth_user(user: User):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username


def logout_user():
    session['logged_in'] = False
    session['user_id'] = None
    session['username'] = None
