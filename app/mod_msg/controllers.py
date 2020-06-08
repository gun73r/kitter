import json

import uuid
from flask import Blueprint, Response, request
from flask.views import MethodView

from app.utils import get_username_token, user_has_token, Encoder
from app.models import User, Chat
from playhouse.shortcuts import model_to_dict as mtd

mod_msg = Blueprint('messages', __name__, url_prefix='/message')


class EnterChatRoom(MethodView):
    def post(self):
        username, token, content = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            companion = content['companion']
            try:
                receiver = User.get(User.username == companion)
                user = User.get(User.username == username)
            except:
                return Response(json.dumps({'message': 'Not Exists'}),
                                status='404')
            room = None
            if not Chat.exists(user, receiver):
                room = Chat.create(from_user=user,
                                   to_user=receiver)
            else:
                room = Chat.get_room(user, receiver)
            return Response(json.dumps({'message': 'OK',
                                        'uuid': room.uuid},
                                       cls=Encoder), status='200')
        return Response(json.dumps({'message': 'Not OK'}),
                        status='401')


class GetChats(MethodView):
    def post(self):
        username, token = get_username_token(request)
        if user_has_token(username, token):
            try:
                user = User.get(User.username == username)
            except:
                return Response(json.dumps({'message': 'Not Exists'}),
                                status='404')
            chats = user.get_chats_with_user()
            return Response(json.dumps({'message': 'OK',
                                        'chats': [(t.uuid,
                                                   mtd(t.from_user if t.to_user == user else t.to_user),
                                                   t.get_last_message().content if t.get_last_message() else None) for t in chats]},
                                       cls=Encoder), status='200')
        return Response(json.dumps({'message': 'Not OK'}),
                        status='401')


class GetMessages(MethodView):
    def post(self):
        username, token, content = get_username_token(request, return_content=True)
        if user_has_token(username, token):
            try:
                chat = Chat.get(Chat.uuid == uuid.UUID(content['uuid']))
            except:
                return Response(json.dumps({'message': 'Not Exists'}),
                                status='404')
            return Response(json.dumps({'message': 'OK',
                                        'messages': [mtd(t) for t in chat.get_messages()]},
                                       cls=Encoder), status='200')
        return Response(json.dumps({'message': 'Not OK'}),
                        status='401')


mod_msg.add_url_rule('/enter_room', view_func=EnterChatRoom.as_view('enter_room'), methods=['POST'])
mod_msg.add_url_rule('/get', view_func=GetChats.as_view('get_chats'), methods=['POST'])
mod_msg.add_url_rule('/get_current', view_func=GetMessages.as_view('get_messages'), methods=['POST'])
