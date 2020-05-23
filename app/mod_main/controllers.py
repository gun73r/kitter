from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

from app.utils import login_required, get_current_user

mod_main = Blueprint('main', __name__)


@mod_main.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return redirect(url_for('main.feed'))
    return redirect(url_for('auth.signin'))


@mod_main.route('/feed', methods=['GET'])
@login_required
def feed():
    user = get_current_user()
    return render_template('feed.html', posts=user.get_feed())
