from flask import Blueprint, request, Response, flash, redirect
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
import json
from playhouse.shortcuts import model_to_dict as mtd
from peewee import *


from app.models import *
from app.utils import auth_user, logout_user, Encoder
from app.mail import *
import app

mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


class SignIn(MethodView):
    def post(self):
        content = request.get_json()
        user = User.get(User.username == content['username'])
        print(content)
        if user and check_password_hash(user.password, content['password']):
            auth_user(user)
            rand_token = uuid4()
            if user.username not in app.token_dct:
                app.token_dct[user.username] = []
            app.token_dct[user.username].append(rand_token)
            chat_rooms = Chat.select(Chat.to_user == user).execute()
            return Response(json.dumps({'message': 'Authorized',
                                        'user': json.dumps(mtd(user), cls=Encoder),
                                        'chat_rooms': json.dumps(mtd(chat_rooms), cls=Encoder),
                                        'followings': json.dumps(mtd(user.get_following()), cls=Encoder),
                                        'followers': json.dumps(mtd(user.get_followers()), cls=Encoder),
                                        'token': rand_token}), status='200')
        else:
            return Response(json.dumps({'message': 'Unauthorised'}), status='401')


class SignUp(MethodView):
    def get(self):
        return Response({'lol': 'kek'})

    def post(self):
        content = request.get_json()
        print(content)
        try:
            with DATABASE.atomic():
                user = User.create(username=content.get('username'),
                                   password=generate_password_hash(content.get('password')),
                                   first_name=content.get('first_name'),
                                   last_name=content.get('last_name'),
                                   email=content.get('email'))
            send_verification(user.email)
            app.app.logger.info('user %s signed up successfully', user.username)
            auth_user(user)
            return Response(json.dumps({'message': 'Available'}), status='200')
        except IntegrityError:
            flash('User with this username already exist')
        return Response(json.dumps({'message': 'Unavailable'}), status='401')


@mod_auth.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.signin'))


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
    return redirect(url_for('main.feed'))


@mod_auth.route('signin_by_token/', methods=[])
def token_sign_in():
    pass


mod_auth.add_url_rule('/signin', view_func=SignIn.as_view('signin'), methods=['POST'])
mod_auth.add_url_rule('/signup', view_func=SignUp.as_view('signup'), methods=['POST', 'GET'])
