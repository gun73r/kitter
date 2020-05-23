from wtforms import Form, TextAreaField
from wtforms.validators import DataRequired


class PostForm(Form):
    content = TextAreaField('Post',
                          [DataRequired(message='You need to write something before post')])
