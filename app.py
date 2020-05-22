from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_admin.contrib.peeweemodel import ModelView
from flask_admin import Admin
from urls import *


from models import *
from utils import get_current_user

app = Flask(__name__)

app.add_url_rule('/login', view_func=Login.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule('/registration', view_func=Registration.as_view('registration'), methods=['GET', 'POST'])
app.add_url_rule('/users/<username>', view_func=UserPage.as_view('users'), methods=['GET', 'POST'])
app.add_url_rule('/posts/<post_id>/edit', view_func=EditPost.as_view('edit_post'), methods=['GET', 'POST'])


admin = Admin(app)
app.config['SECRET_KEY'] = environ['SECRET']

admin.add_view(ModelView(User))
admin.add_views(ModelView(Post))
admin.add_views(ModelView(Message))
admin.add_views(ModelView(Like))
admin.add_views(ModelView(Follow))


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


if __name__ == '__main__':
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
