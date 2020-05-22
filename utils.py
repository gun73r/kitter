from functools import wraps
from flask import redirect, url_for, session
from models import *


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session['logged_in']:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session['logged_in'] or not get_current_user().is_admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper


def get_current_user():
    if session.get('logged_in'):
        return User.get(User.id == session.get('user_id'))


def auth_user(user: User):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username