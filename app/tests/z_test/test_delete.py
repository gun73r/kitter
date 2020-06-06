from app import User


def test_delete(new_user, new_user_first, new_user_second):
    new_user.delete_instance()
    new_user_second.delete_instance()
    new_user_first.delete_instance()
    assert isinstance(new_user, User)
