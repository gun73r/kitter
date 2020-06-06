from flask_mail import Message
from flask import render_template, url_for
from itsdangerous import URLSafeTimedSerializer
from multiprocessing import Process
import app


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.app.config['SECURITY_PASSWORD_SALT'])


def token_to_email(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def _send_verification(to_email):
    token = generate_confirmation_token(to_email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('auth/activate.html', confirm_url=confirm_url)
    with app.app.app_context():
        msg = Message(subject='Please confirm your email',
                      sender='kitter.noreply@gmail.com',
                      recipients=[to_email],
                      html=html)
        app.mail.send(msg)
    app.app.logger.info('email to %s sent successfully', to_email)


proc_list = []


def send_verification(to_email):
    p = Process(target=_send_verification, args=(to_email, ))
    proc_list.append(p)
    p.start()
    p.join()


