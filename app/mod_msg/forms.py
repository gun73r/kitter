from wtforms import Form, TextAreaField
from wtforms.validators import DataRequired


class MessageForm(Form):
    content = TextAreaField('Message',
                            [DataRequired(message='Type at least 1 character to send')])
