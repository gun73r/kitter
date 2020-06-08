import datetime
import json

from flask_socketio import emit, join_room, close_room
from playhouse.shortcuts import model_to_dict as mtd

from app.models import User, Message, Chat
from app.utils import Encoder


def on_connect():
    emit('connect', {'statusCode': 200})


def create_room(data):
    join_room(data['username'])


def leave_room(data):
    close_room(data['username'])


def message(data):
    username = data['username']
    uuid = data['uuid']
    try:
        sender = User.get(User.username == username)
    except:
        return
    chats = Chat.get_chats_with_user(sender)
    if len(chats) == 0:
        return
    receiver = chat = None
    for c in chats:
        if str(c.uuid) == uuid:
            chat = c
            if c.from_user == sender:
                receiver = c.to_user
            else:
                receiver = c.from_user
    if not receiver or not chat:
        return
    msg = Message.create(user=sender,
                         chat=chat,
                         content=data['text'])
    chat.update(last_interaction=datetime.datetime.now()).execute()
    emit('new_message', {'message': json.dumps(mtd(msg), cls=Encoder)}, room=receiver.username)
    emit('new_message', {'message': json.dumps(mtd(msg), cls=Encoder)}, room=sender.username)
