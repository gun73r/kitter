import json

from flask import Blueprint, request, Response
from flask.views import MethodView
from playhouse.shortcuts import model_to_dict as mtd

from app.models import Like, Post, User
from app.utils import user_has_token, get_username_token, Encoder

mod_post = Blueprint('posts', __name__, url_prefix='/posts')


class LikePost(MethodView):
    def post(self):
        username, token, content = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            try:
                post = Post.get(Post.uuid == content['uuid'])
                user = User.get(User.username == username)
            except:
                return Response(json.dumps({'message': 'Not Exist'}), status='404')
            if Post.like_exists(user, post):
                Like.get((Like.user == user) & (Like.post == post)).delete_instance()
            else:
                Like.create(user=user,
                            post=post)
            return Response(json.dumps({'message': 'OK'}), status='200')
        return Response(json.dumps({'message': 'Not OK'}), status='401')


class RemovePost(MethodView):
    def post(self):
        username, token, content = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            try:
                post = Post.get(Post.uuid == content['uuid'])
            except:
                return Response(json.dumps({'message': 'Not Exist'}), status='404')
            post.delete_instance()
            return Response(json.dumps({'message': 'OK'}), status='200')
        return Response(json.dumps({'message': 'Not OK'}), status='401')


class AddPost(MethodView):
    def post(self):
        username, token, j = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            content = j['content']['text']
            user = User.get(User.username == username)
            post = Post.create(user=user,
                               content=content)
            return Response(json.dumps({'message': 'OK'}), status='200')
        return Response(json.dumps({'message': 'Not OK'}), status='401')


class UserFeed(MethodView):
    def post(self):
        username, token = get_username_token(request)
        if user_has_token(username, token):
            user = User.get(User.username == username)
            return Response(json.dumps({'message': 'OK',
                                        'posts': [(mtd(p), p.get_likes(), Post.like_exists(user, p)) for p in user.get_feed()]},
                                       cls=Encoder), status='200')
        return Response(json.dumps({'message': 'Not OK'}),
                        status='401')


mod_post.add_url_rule('/delete', view_func=RemovePost.as_view('delete_post'), methods=['POST'])
mod_post.add_url_rule('/add', view_func=AddPost.as_view('add_post'), methods=['POST'])
mod_post.add_url_rule('/like', view_func=LikePost.as_view('like_post'), methods=['POST'])
mod_post.add_url_rule('/feed', view_func=UserFeed.as_view('user_feed'), methods=['POST'])
