from wtforms import Form, TextAreaField
from wtforms.validators import DataRequired


class EditPostForm(Form):
    content = TextAreaField('Edit Post',
                            [DataRequired(message='Your post should contain at least one character')])
