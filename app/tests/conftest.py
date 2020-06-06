import pytest

from app import create_app
from app.models import User


@pytest.fixture
def app():
    return create_app()


@pytest.fixture(scope='session')
def new_user():
    return User.create(username='test_user',
                       password='testpassword',
                       email='test@email.com',
                       first_name='Test',
                       last_name='User')


@pytest.fixture(scope='session')
def new_user_first():
    return User.create(username='test_user_first',
                       password='testpassword',
                       email='test_first@email.com',
                       first_name='Test',
                       last_name='User')


@pytest.fixture(scope='session')
def new_user_second():
    return User.create(username='test_user_second',
                       password='testpassword',
                       email='test_second@email.com',
                       first_name='Test',
                       last_name='User')

