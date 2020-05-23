from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from peewee import IntegrityError

from app.models import User, DATABASE, Message
from app.utils import get_current_user, login_required
from app.mod_msg.forms import MessageForm


mod_msg = Blueprint('messages', __name__, url_prefix='/message')


@mod_msg.route('/to/<username>', methods=['GET'])
@login_required
def message_to(username):
    form = MessageForm()
    user = User.get(User.username == username)
    messages = get_current_user().get_messages_with_user(user)
    return render_template('msg/chat_page.html', messages=messages, to_user=user, form=form)


@mod_msg.route('/to/<username>/send', methods=['POST'])
@login_required
def send_message_to(username):
    user = User.get(User.username == username)
    if request.form.get('content') != '':
        try:
            with DATABASE.atomic():
                print(Message.create(from_user=get_current_user(),
                                     to_user=user,
                                     content=request.form.get('content')))
        except IntegrityError:
            flash('something went wrong')
    return redirect(request.referrer)
