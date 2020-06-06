from flask import Blueprint, Response, session, redirect, url_for

from app.utils import login_required, get_current_user
from app.models import Post, User

mod_main = Blueprint('main', __name__)


@mod_main.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return redirect(url_for('main.feed'))
    return redirect(url_for('auth.signin'))


@mod_main.route('/feed', methods=['POST'])
@login_required
def feed():
    posts = Post.get(Post.user == get_current_user().get_following())
    return Response({'message': 'Authorized',
                     'user_posts': Post.get_delete_put_post(posts)})
