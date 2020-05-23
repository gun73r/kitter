from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.views import MethodView
from peewee import IntegrityError


from app.models import User, Post, DATABASE, Follow
from app.utils import get_current_user, login_required
from app.mod_user.forms import PostForm

mod_user = Blueprint('users', __name__, url_prefix='/users')


class UserPage(MethodView):
    def get(self, username):
        form = PostForm()
        user = User.get(User.username == username)
        if user is None:
            return redirect(url_for('main.feed'))
        return render_template('user/user_page.html', user=user, form=form)

    def post(self, username):
        form = PostForm()
        user = User.get(User.username == username)
        Post.create(user=get_current_user(),
                    content=request.form.get('content'))
        return render_template('user/user_page.html', user=user, form=form)


@mod_user.route('/<username>/following', methods=['GET'])
@login_required
def following(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect(url_for('main.feed'))
    return render_template('user/follow_page.html', page_type='following', user_list=user.get_following())


@mod_user.route('/<username>/followers', methods=['GET'])
@login_required
def followers(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect(url_for('main.feed'))
    return render_template('user/follow_page.html', page_type='followers', user_list=user.get_followers())


@mod_user.route('/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect('main.feed')
    try:
        with DATABASE.atomic():
            Follow.create(from_user=get_current_user(), to_user=user)
    except IntegrityError:
        pass
    return redirect(url_for('users.user_page', username=user.username))


@mod_user.route('/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect('main.feed')
    Follow.delete().where((Follow.from_user == get_current_user())
                          & (Follow.to_user == user)).execute()
    return redirect(url_for('users.user_page', username=user.username))


mod_user.add_url_rule('/<username>', view_func=UserPage.as_view('user_page'), methods=['GET', 'POST'])
