from app.utils import *
from flask import session
from app import app


def test_utils(new_user):
    with app.test_request_context():
        auth_user(new_user)
        assert session.get('user_id') == new_user.id
        assert session.get('logged_in')
        assert session.get('username') == new_user.username
        assert get_current_user() == new_user
        logout_user()
        assert session.get('user_id') is None
        assert not session.get('logged_in')
        assert session.get('username') is None
        assert get_current_user() is None
