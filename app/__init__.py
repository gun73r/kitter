from logging.config import dictConfig
from flask import Flask, request
from flask_admin.contrib.peewee import ModelView
from flask_admin import Admin
from flask_mail import Mail

from app.models import *
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_user.controllers import mod_user as user_module
from app.mod_post.controllers import mod_post as post_module
from app.mod_msg.controllers import mod_msg as message_module
from app.mod_main.controllers import mod_main as main_module
from app.utils import get_current_user
from config import mail_settings


def create_app():
    _app = Flask(__name__)
    _app.config.from_object('config')
    _app.config.update(mail_settings)
    _app.register_blueprint(auth_module)
    _app.register_blueprint(user_module)
    _app.register_blueprint(post_module)
    _app.register_blueprint(message_module)
    _app.register_blueprint(main_module)

    admin = Admin(_app)
    admin.add_view(ModelView(User))
    admin.add_views(ModelView(Post))
    admin.add_views(ModelView(Message))
    admin.add_views(ModelView(Like))
    admin.add_views(ModelView(Follow))

    return _app


app = create_app()


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


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

