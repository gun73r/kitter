from wtforms import Form, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo


class SignInForm(Form):
    username = StringField('Username',
                           [DataRequired(message='Forgot your username?')])
    password = PasswordField('Password',
                             [DataRequired(message='You must provide a password')])


class SignUpForm(Form):
    username = StringField('Username',
                           [DataRequired(message='Forgot your username?')])
    email = StringField('Email Address',
                        [Email(),
                         DataRequired(message='Forgot your email address?')])
    password = PasswordField('Password',
                             [DataRequired(message='You must provide a password')])
    repeat_password = PasswordField('Repeat password',
                                    [DataRequired(message='You must provide a repeat password'),
                                     EqualTo('password', 'Passwords do not match')])
    first_name = StringField('First Name',
                             [DataRequired(message='You must provide a first name')])
    last_name = StringField('Last Name',
                            [DataRequired(message='You must provide a last name')])

