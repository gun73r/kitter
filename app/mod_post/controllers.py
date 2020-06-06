from flask import Blueprint, request, render_template, redirect, url_for, Response
from flask.views import MethodView
from peewee import IntegrityError

from app.mod_post.forms import EditPostForm
from app.models import DATABASE, Like, Post
from app.utils import get_current_user, login_required


mod_post = Blueprint('posts', __name__, url_prefix='/posts')


@mod_post.route('/posts/<post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.get(Post.id == post_id)
    try:
        like = Like.get((Like.post == post) & (Like.user == get_current_user()))
        liked = True
    except:
        liked = False

    if not liked:
        try:
            with DATABASE.atomic():
                Like.create(post=post, user=get_current_user())
                return Response({'message': 'Liked'}, status='200')
        except IntegrityError:
            return Response({'message': 'Failed'}, status='400')
    like.delete_instance()
    return Response({'message': 'Unliked'})


class EditPost(MethodView):
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
    post.delete_instance()
    return Response({'message': 'Success'})


mod_post.add_url_rule('/<post_id>/edit', view_func=EditPost.as_view('edit_post'), methods=['GET', 'POST'])
