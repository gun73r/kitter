from app.models import *


def test_new_user(new_user):
    assert new_user.email == 'test@email.com'
    assert new_user.password == 'testpassword'
    assert not new_user.is_admin
    assert not new_user.verified
    assert new_user.username == 'test_user'
    assert new_user.first_name == 'Test'
    assert new_user.last_name == 'User'
    assert len(new_user.get_posts()) == 0
    assert len(new_user.get_followers()) == 0
    assert len(new_user.get_following()) == 0
    assert len(new_user.get_feed()) == 0


def test_new_post(new_user):
    post = Post.create(user=new_user,
                       content='content')
    assert post.user == new_user
    assert post.content == 'content'
    post.delete_instance()


def test_new_follow(new_user_first, new_user_second):
    follow = Follow.create(from_user=new_user_first,
                           to_user=new_user_second)
    assert follow.from_user != new_user_second
    assert follow.from_user == new_user_first
    assert follow.to_user == new_user_second
    assert follow.to_user != new_user_first
    follow.delete_instance()


def test_like(new_user_first, new_user_second):
    post = Post.create(user=new_user_first,
                       content='content')
    like = Like.create(user=new_user_second,
                       post=post)
    assert like.post == post
    assert like.user == new_user_second
    like.delete_instance()
    post.delete_instance()
