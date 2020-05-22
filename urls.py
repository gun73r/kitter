from flask.views import MethodView
from flask import request, flash, render_template, redirect, url_for, session
from utils import *
from passlib.hash import sha512_crypt
from app import app


@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return redirect(url_for('feed'))
    return redirect(url_for('login'))


class Login(MethodView):
    def get(self):
        return render_template('login.html')

    def post(self):
        try:
            ph = sha512_crypt.encrypt(request.form.get('password'))
            user = User.get((User.password == ph) &
                            (User.username == request.form.get('username')))
        except User.DoesNotExist:
            flash('Username or password are incorrect')
        else:
            auth_user(user)
            return redirect(url_for('feed'))


class Registration(MethodView):
    def get(self):
        return render_template('registration.html')

    def post(self):
        if request.form.get('password') != request.form.get('repeat_password'):
            flash('Passwords do not match')
            return render_template('registration.html')
        try:
            with DATABASE.atomic():
                user = User.create(username=request.form.get('username'),
                                   password=sha512_crypt.encrypt(request.form.get('password')),
                                   first_name=request.form.get('first_name'),
                                   last_name=request.form.get('last_name'),
                                   email=request.form.get('email'))
                auth_user(user)
                return redirect(url_for('feed'))
        except IntegrityError:
            flash('User with this username already exist')


@app.route('/feed', methods=['GET'])
@login_required
def feed():
    user = get_current_user()
    return render_template('feed.html', posts=user.get_feed())


@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


class UserPage(MethodView):
    def get(self, username):
        user = User.get(User.username == username)
        if user is None:
            return redirect(url_for('feed'))
        return render_template('user_page.html', user=user)

    def post(self, username):
        user = User.get(User.username == username)
        Post.create(user=get_current_user(),
                    content=request.form.get('content'))
        return render_template('user_page.html', user=user)


@app.route('/users/<username>/following', methods=['GET'])
@login_required
def following(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect(url_for('feed'))
    return render_template('follow_page.html', page_type='following', user_list=user.get_following())


@app.route('/users/<username>/followers', methods=['GET'])
@login_required
def followers(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect(url_for('feed'))
    return render_template('follow_page.html', page_type='followers', user_list=user.get_followers())


@app.route('/users/<username>/follow', methods=['POST'])
@login_required
def follow(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect('feed')
    try:
        with DATABASE.atomic():
            Follow.create(from_user=get_current_user(), to_user=user)
    except IntegrityError:
        pass
    return redirect(url_for('user_page', username=user.username))


@app.route('/users/<username>/unfollow', methods=['POST'])
@login_required
def unfollow(username):
    user = User.get(User.username == username)
    if user is None:
        return redirect('feed')
    Follow.delete().where((Follow.from_user == get_current_user())
                          & (Follow.to_user == user)).execute()
    return redirect(url_for('user_page', username=user.username))


@app.route('/posts/<post_id>', methods=['GET'])
@login_required
def post_page(post_id):
    post = Post.get(Post.id == post_id)
    return render_template('post_page.html', post=post)


@app.route('/posts/<post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.get(Post.id == post_id)
    try:
        with DATABASE.atomic():
            Like.create(post=post, user=get_current_user())
    except IntegrityError:
        pass
    return redirect(request.referrer)


@app.route('/posts/<post_id>/unlike', methods=['POST'])
@login_required
def unlike_post(post_id):
    post = Post.get(Post.id == post_id)
    Like.delete().where((Like.post == post) & (Like.user == get_current_user())).execute()
    return redirect(request.referrer)


class EditPost(MethodView):
    def get(self, post_id):
        post = Post.get(Post.id == post_id)
        return render_template('edit_post.html', post=post)

    def post(self, post_id):
        post = Post.get(Post.id == post_id)
        if request.form.get('content') and request.method == 'POST':
            content = request.form.get('content')
            Post.update(content=content).where(Post.id == post.id).execute()
            return redirect(url_for('user_page', user=post.user, username=post.user.username))
        if not request.form.get('content'):
            flash('your post should take 1 letter at least')


@app.route('/posts/<post_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_post(post_id):
    pass


@app.route('/posts/<post_id>/remove', methods=['POST'])
@login_required
def remove_post(post_id):
    post = Post.get(Post.id == post_id)
    Like.delete().where(Like.post == post).execute()
    Post.delete().where(Post.id == post.id).execute()
    return redirect(request.referrer)


@app.route('/message/to/<username>', methods=['GET'])
@login_required
def message_to(username):
    user = User.get(User.username == username)
    messages = get_current_user().get_messages_with_user(user)
    return render_template('chat_page.html', messages=messages, to_user=user)


@app.route('/message/to/<username>/send', methods=['POST'])
@login_required
def send_message_to(username):
    user = User.get(User.username == username)
    print(request.form.get('content'))
    if request.form.get('content') != '':
        try:
            with DATABASE.atomic():
                print(Message.create(from_user=get_current_user(),
                                     to_user=user,
                                     content=request.form.get('content')))
        except IntegrityError:
            flash('something went wrong')
    return redirect(request.referrer)


@app.route('/test')
@admin_required
def test():
    create_tables()
    return redirect(url_for('index'))
    # User.update(password=sha512_crypt.encrypt('Sanek12062001')).where(User.username == 'gun73r').execute()
    # messages = Message.select()
    # return render_template('test.html', messages=messages)
