from app.mail import *


def test_token():
    email = 'test@email.com'
    token = generate_confirmation_token(email)
    assert token_to_email(token) == email
