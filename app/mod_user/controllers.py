import json

from flask import Blueprint, request, Response
from flask.views import MethodView
from playhouse.shortcuts import model_to_dict as mtd

from app.models import User, Post, Follow
from app.utils import user_has_token, Encoder, get_username_token

mod_user = Blueprint('users', __name__, url_prefix='/users')


class GetProfile(MethodView):
    def post(self):
        username, token, content = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            current_user = User.get(User.username == username)
            user = User.get(User.username == content['query'])
            return Response(json.dumps({'message': 'OK',
                                        'user': mtd(user),
                                        'following': [mtd(t) for t in user.get_following()],
                                        'followers': [mtd(t) for t in user.get_followers()],
                                        'posts': [(mtd(t), t.get_likes(), Post.like_exists(current_user, t))
                                                  for t in user.get_posts()]},
                                       cls=Encoder), status='200')
        return Response(json.dumps({'message': 'Error'}), status='401')


class SearchUser(MethodView):
    def post(self):
        username, token, content = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            user = User.get(User.username == username)
            return Response(json.dumps({'message': 'OK',
                                        'users': [(mtd(t), user.you_follow(t)) for t in User.search_by_username(content['query'])]},
                                       cls=Encoder), status='200')
        return Response(json.dumps({'message': 'Not OK'}), status='401')


class FollowUser(MethodView):
    def post(self):
        username, token, content = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            try:
                follow_user = User.get(User.username == content['query'])
                user = User.get(User.username == username)
            except:
                return Response(json.dumps({'message': 'Not Exist'}), status='404')
            if user.you_follow(follow_user):
                Follow.get((Follow.to_user == follow_user) & (Follow.from_user == user)).delete_instance()
            else:
                Follow.create(from_user=user,
                              to_user=follow_user)
            return Response(json.dumps({'message': 'OK'}), status='200')
        return Response(json.dumps({'message': 'Not OK'}), status='401')


mod_user.add_url_rule('/get_profile', view_func=GetProfile.as_view('get_profile'), methods=['POST'])
mod_user.add_url_rule('/search', view_func=SearchUser.as_view('search_user'), methods=['Post'])
mod_user.add_url_rule('/follow', view_func=FollowUser.as_view('follow_user'), methods=['POST'])
