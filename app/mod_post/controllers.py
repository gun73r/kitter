from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.views import MethodView
from peewee import IntegrityError

from app.mod_post.forms import EditPostForm
from app.models import User, DATABASE, Like, Post
from app.utils import get_current_user, login_required


mod_post = Blueprint('posts', __name__, url_prefix='/posts')


@mod_post.route('/<post_id>', methods=['GET'])
@login_required
def post_page(post_id):
    post = Post.get(Post.id == post_id)
    return render_template('post/post_page.html', post=post)


@mod_post.route('/posts/<post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.get(Post.id == post_id)
    try:
        with DATABASE.atomic():
            Like.create(post=post, user=get_current_user())
    except IntegrityError:
        pass
    return redirect(request.referrer)


@mod_post.route('/posts/<post_id>/unlike', methods=['POST'])
@login_required
def unlike_post(post_id):
    post = Post.get(Post.id == post_id)
    Like.delete().where((Like.post == post) & (Like.user == get_current_user())).execute()
    return redirect(request.referrer)


class EditPost(MethodView):
    @login_required
    def get(self, post_id):
        form = EditPostForm(request.form)
        post = Post.get(Post.id == post_id)
        form.content.data = post.content
        return render_template('post/edit_post.html', post=post, form=form)

    @login_required
    def post(self, post_id):
        form = EditPostForm(request.form)
        post = Post.get(Post.id == post_id)
        if form.validate():
            content = request.form.get('content')
            Post.update(content=content).where(Post.id == post.id).execute()
            return redirect(url_for('users.user_page', user=post.user, username=post.user.username))
        return redirect(request.referrer)


@mod_post.route('/<post_id>/remove', methods=['POST'])
@login_required
def remove_post(post_id):
    post = Post.get(Post.id == post_id)
    Like.delete().where(Like.post == post).execute()
    Post.delete().where(Post.id == post.id).execute()
    return redirect(request.referrer)


mod_post.add_url_rule('/<post_id>/edit', view_func=EditPost.as_view('edit_post'), methods=['GET', 'POST'])
