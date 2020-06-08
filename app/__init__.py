from flask import Flask, request
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
from flask_cors import CORS
from flask_mail import Mail
from flask_socketio import SocketIO

import app.mod_msg.events as events
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_msg.controllers import mod_msg as message_module
from app.mod_post.controllers import mod_post as post_module
from app.mod_user.controllers import mod_user as user_module
from app.models import *
from app.utils import get_current_user
from config import mail_settings

token_dct = {}


def create_app():
    _app = Flask(__name__)
    _app.config.from_object('config')
    _app.config.update(mail_settings)
    bps = [auth_module, user_module, post_module, message_module]
    for m in bps:
        CORS(m)
        _app.register_blueprint(m)

    admin = Admin(_app)
    admin.add_view(ModelView(User))
    admin.add_views(ModelView(Post))
    admin.add_views(ModelView(Message))
    admin.add_views(ModelView(Like))
    admin.add_views(ModelView(Follow))
    admin.add_views(ModelView(Chat))
    return _app


app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")
socketio.init_app(app)
socketio.on_event('connect', events.on_connect)
socketio.on_event('create_room', events.create_room)
socketio.on_event('close_room', events.leave_room)
socketio.on_event('new_message', events.message)
CORS(app)


@app.context_processor
def _current_user():
    return {'current_user': get_current_user()}


@app.context_processor
def _current_link():
    return {'current_link': request.url}


@app.template_filter('liked_by')
def _liked_by(_post: Post, user: User):
    return _post.liked_by(user)


@app.template_filter('is_following')
def is_following(from_user: User, to_user: User):
    return from_user.is_following(to_user)


@app.template_filter('is_admin')
def _is_admin(user: User):
    return user.is_admin


mail = Mail(app)
