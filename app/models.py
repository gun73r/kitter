import datetime
import uuid

from flask_login import UserMixin
from peewee import *

import config

DATABASE = PostgresqlDatabase(config.DATABASE_NAME,
                              user=config.DATABASE_USER,
                              password=config.DATABASE_PASSWORD,
                              host=config.DATABASE_HOST,
                              port=5432)


class BaseModel(Model):
    class Meta:
        database = DATABASE


class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField(max_length=128)
    join_date = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    verified = BooleanField(default=False)

    class Meta:
        order_by = ('-joined_at',)

    def get_posts(self):
        return list(Post.select().join(User).where(Post.user.id == self.id).order_by(Post.pub_date.desc()).execute())

    def get_followers(self):
        return list(User.select().join(Follow, on=Follow.from_user)
                    .where(Follow.to_user == self).execute())

    def get_following(self):
        return list(User.select().join(Follow, on=Follow.to_user)
                    .where(Follow.from_user == self).execute())

    def you_follow(self, user):
        return Follow.select().join(User, on=(Follow.to_user == user.id)).where(Follow.from_user == self.id).exists()

    def get_feed(self):
        return list(Post.select().where((Post.user << self.get_following()) | (Post.user == self))
                    .order_by(Post.pub_date.desc()).execute())

    def get_messages_with_user(self, user):
        return Message.select().where(((Message.from_user == self) & (Message.to_user == user))
                                      | ((Message.from_user == user) & (Message.to_user == self)))

    @classmethod
    def search_by_username(cls, username):
        return list(User.select().where(User.username.contains(username)).execute())


class Post(BaseModel):
    pub_date = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(User, backref='posts')
    uuid = UUIDField(default=uuid.uuid4, verbose_name='UUID')
    content = TextField()

    class Meta:
        order_by = ('-post_time',)

    def get_likes(self):
        return len(list(Like.select().join(Post, on=(Like.post == Post.id))
                        .where(Like.post.id == self.id).execute()))

    @classmethod
    def like_exists(cls, user, post):
        return Like.select().where((Like.user == user) & (Like.post == post)).exists()


class Like(BaseModel):
    user = ForeignKeyField(User, backref='likes')
    post = ForeignKeyField(Post, backref='likes', on_delete='CASCADE')


class Follow(BaseModel):
    from_user = ForeignKeyField(User, backref='from')
    to_user = ForeignKeyField(User, backref='to')
    follow_date = DateTimeField(default=datetime.datetime.now())


class Chat(BaseModel):
    uuid = UUIDField(null=False, unique=True, verbose_name='UUID')
    to_user = ForeignKeyField(User, backref='reciever')


class Message(BaseModel):
    pub_date = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(User, backref='messages')
    chat = ForeignKeyField(Chat, on_delete='CASCADE')
    content = TextField()


class LoginDevices(BaseModel):
    token = CharField(max_length=64, unique=True)
    user = ForeignKeyField(User, backref='has_token')


def create_tables():
    DATABASE.create_tables([User, Post, Message, Like, Follow, Chat, LoginDevices])


def drop_tables():
    DATABASE.drop_tables([User, Post, Message, Like, Follow, Chat, LoginDevices])
