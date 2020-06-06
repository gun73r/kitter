from flask import Blueprint, request, Response, flash, session, redirect
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4

from app.mod_auth.forms import *
from app.models import *
from app.utils import auth_user, logout_user
from app.mail import *
import app

mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


class SignIn(MethodView):
    def post(self):
        form = SignInForm(request.form)
        app.app.logger.info(form.csrf_token)
        if form.validate():
            user = User.get(User.username == form.username.data)
            if user and check_password_hash(user.password, form.password.data):
                auth_user(user)
                rand_token = uuid4()
                if user.username not in app.token_dct:
                    app.token_dct[user.username] = []
                app.token_dct[user.username].append(rand_token)
                chat_rooms = Chat.select(Chat.to_user == user).execute()
                return Response({'message': 'Authorized',
                                 'user': User.get_delete_put_post(user),
                                 'chat_rooms': Chat.get_delete_put_post(chat_rooms),
                                 'followings': Follow.get_delete_put_post(user.get_following()),
                                 'followers': Follow.get_delete_put_post(user.get_followers())}, status='200')
            else:
                return Response({'message': 'Unauthorised'}, status='401')
        flash('Wrong username or password')


class SignUp(MethodView):
    def post(self):
        form = SignUpForm(request.form)
        if form.validate():
            try:
                with DATABASE.atomic():
                    user = User.create(username=request.form.get('username'),
                                       password=generate_password_hash(request.form.get('password')),
                                       first_name=request.form.get('first_name'),
                                       last_name=request.form.get('last_name'),
                                       email=request.form.get('email'))
                send_verification(user.email)
                app.app.logger.info('user %s signed up successfully', user.username)
                auth_user(user)
                return Response({'message': 'Available'}, status='200')
            except IntegrityError:
                flash('User with this username already exist')
        for err, it in form.errors.items():
            flash(it)
        return redirect(url_for('auth.signup'))


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


mod_auth.add_url_rule('/signin', view_func=SignIn.as_view('signin'), methods=['POST'])
mod_auth.add_url_rule('/sigup', view_func=SignUp.as_view('signup'), methods=['POST'])
