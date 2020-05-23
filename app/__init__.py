from flask import Flask, request
from flask_admin.contrib.peewee import ModelView
from flask_admin import Admin

from app.models import *
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_user.controllers import mod_user as user_module
from app.mod_post.controllers import mod_post as post_module
from app.mod_msg.controllers import mod_msg as message_module
from app.mod_main.controllers import mod_main as main_module
from app.utils import get_current_user

app = Flask(__name__)
app.config.from_object('config')
app.register_blueprint(auth_module)
app.register_blueprint(user_module)
app.register_blueprint(post_module)
app.register_blueprint(message_module)
app.register_blueprint(main_module)


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


admin = Admin(app)
admin.add_view(ModelView(User))
admin.add_views(ModelView(Post))
admin.add_views(ModelView(Message))
admin.add_views(ModelView(Like))
admin.add_views(ModelView(Follow))
