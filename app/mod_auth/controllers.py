from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.views import MethodView
from peewee import IntegrityError

from werkzeug.security import generate_password_hash, check_password_hash
from app.mod_auth.forms import *
from app.models import User, DATABASE
from app.utils import auth_user, logout_user

mod_auth = Blueprint('auth', __name__, url_prefix='/auth')


class SignIn(MethodView):
    def get(self):
        form = SignInForm(request.form)
        return render_template('auth/signin.html', form=form)

    def post(self):
        form = SignInForm(request.form)
        if form.validate():
            user = User.get(User.username == form.username.data)
            if user and check_password_hash(user.password, form.password.data):
                auth_user(user)
                return redirect(url_for('main.feed'))
            flash('Wrong username or password')


class SignUp(MethodView):
    def get(self):
        form = SignUpForm(request.form)
        return render_template('auth/sigup.html', form=form)

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
                auth_user(user)
                return redirect(url_for('auth.signin'))
            except IntegrityError:
                flash('User with this username already exist')
        for err, it in form.errors.items():
            flash(it)
        return redirect(url_for('auth.signup'))


@mod_auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('login'))


mod_auth.add_url_rule('/signin', view_func=SignIn.as_view('signin'), methods=['GET', 'POST'])
mod_auth.add_url_rule('/sigup', view_func=SignUp.as_view('signup'), methods=['GET', 'POST'])
