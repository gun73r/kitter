import json
from uuid import uuid4

from flask import Blueprint, request, Response, flash, redirect
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash

import app
from app.mail import *
from app.models import *
from app.utils import auth_user, user_has_token, get_username_token

mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


class SignIn(MethodView):
    def post(self):
        content = request.get_json()
        user = User.get(User.username == content['username'])
        if user and check_password_hash(user.password, content['password']):
            auth_user(user)
            rand_token = str(uuid4())
            if user.username not in app.token_dct:
                app.token_dct[user.username] = []
            app.token_dct[user.username].append(rand_token)
            # chat_rooms = Chat.select(Chat.to_user == user).execute()
            return Response(json.dumps({'message': 'Authorized',
                                        'username': user.username,
                                        'email': user.email,
                                        'token': str(rand_token)}), status='200')
        else:
            return Response(json.dumps({'message': 'Unauthorised'}), status='401')


class SignUp(MethodView):
    def post(self):
        content = request.get_json()
        try:
            with DATABASE.atomic():
                user = User.create(username=content.get('username'),
                                   password=generate_password_hash(content.get('password')),
                                   first_name=content.get('first_name'),
                                   last_name=content.get('last_name'),
                                   email=content.get('email'))
            send_verification(user.email)
            auth_user(user)
            return Response(json.dumps({'message': 'Available'}), status='200')
        except IntegrityError:
            flash('User with this username already exist')
        return Response(json.dumps({'message': 'Unavailable'}), status='401')


class Logout(MethodView):
    def post(self):
        username, token = get_username_token(request)
        if username in app.token_dct:
            if token in app.token_dct[username]:
                app.token_dct[username].remove(token)
                return Response(json.dumps({'message': 'OK'}), status='200')
            return Response(json.dumps({'message': 'Not OK'}), status='401')
        return Response(json.dumps({'message': 'Not OK'}), status='401')


@mod_auth.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = token_to_email(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = User.get(User.email == email)
    if user.verified:
        flash('Account already verified.', 'success')
    else:
        user.verified = True
        user.save()
        flash('You have verified your account. Thanks!', 'success')
    return redirect(url_for('auth.signin'))


class ValidateToken(MethodView):
    def post(self):
        username, token = get_username_token(request)
        if user_has_token(username, token):
            return Response(json.dumps({'message': 'OK'}), status='200')
        return Response(json.dumps({'message': 'Not OK'}), status='401')


mod_auth.add_url_rule('/signin', view_func=SignIn.as_view('signin'), methods=['POST'])
mod_auth.add_url_rule('/signup', view_func=SignUp.as_view('signup'), methods=['POST'])
mod_auth.add_url_rule('/validate_token', view_func=ValidateToken.as_view('validate_token'), methods=['POST'])
mod_auth.add_url_rule('/logout', view_func=Logout.as_view('logout'), methods=['POST'])
