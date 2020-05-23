from flask_login import UserMixin
from peewee import *
import datetime
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

    class Meta:
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().join(User).where(Post.user.id == self.id).order_by(Post.pub_date.desc())

    def get_followers(self):
        return User.select().join(Follow, on=Follow.from_user) \
            .where(Follow.to_user == self)

    def get_following(self):
        return User.select().join(Follow, on=Follow.to_user) \
            .where(Follow.from_user == self)

    def is_following(self, user):
        return Follow.select().where((Follow.from_user == self) & (Follow.to_user == user)).exists()

    def get_feed(self):
        return (Post.select().where((Post.user << self.get_following()) | (Post.user == self))
                .order_by(Post.pub_date.desc()))

    def get_messages_with_user(self, user):
        return Message.select().where(((Message.from_user == self) & (Message.to_user == user))
                                      | ((Message.from_user == user) & (Message.to_user == self)))


class Post(BaseModel):
    pub_date = DateTimeField(default=datetime.datetime.now())
    user = ForeignKeyField(User, backref='posts')
    content = TextField()

    class Meta:
        order_by = ('-post_time',)

    def get_likes_count(self):
        return User.select().join(Like, on=Like.user).where(Post.user == self.user).count

    def get_likers(self):
        return User.select().join(Like, on=Like.user).where(Post.user == self.user)

    def liked_by(self, user: User):
        return Like.select().where((Like.post == self) & (Like.user == user)).exists()


class Message(BaseModel):
    pub_date = DateTimeField(default=datetime.datetime.now())
    from_user = ForeignKeyField(User, backref='send')
    to_user = ForeignKeyField(User, backref='receive')
    content = TextField()


class Like(BaseModel):
    user = ForeignKeyField(User, backref='likes')
    post = ForeignKeyField(Post, backref='likes')


class Follow(BaseModel):
    from_user = ForeignKeyField(User, backref='from')
    to_user = ForeignKeyField(User, backref='to')
    follow_date = DateTimeField(default=datetime.datetime.now())


def create_tables():
    DATABASE.create_tables([User, Post, Message, Like, Follow])
