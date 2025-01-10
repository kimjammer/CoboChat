import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from cobochat import app, db, bcrypt
from cobochat.models import User, Post, Announcement
from cobochat.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, AnnouncementForm
from flask_login import login_user, current_user, logout_user, login_required

# I don't know why this works or why its needed but it fixes like 30 mins worth of errors with the database...
app.app_context().push()

# ======================================
# ========== Helper Functions ==========
# ======================================

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# ====================================
# ========== General Routes ==========
# ====================================

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', title='Home', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/chat_room")
def chat_room():
    return render_template('chat_room.html', title='Chat Room')

@app.route("/display_users")
@login_required
def display_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=10)
    return render_template('display_users.html', title='CoboChat Users', users=users)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') # Redirect back to the page a user was originally trying to get to
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger mt-4')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required # Makes it so that the user must be logged in to view the account page (VERY USEFUL FOR OTHER PARTS OF THE BLOG DONT FORGET THIS COHEN I SWEAR)
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Account has been updated!', 'success mt-4')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post has been created!', 'success mt-4')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author == current_user or current_user.account_type == 'Owner' or current_user.account_type == 'Administrator':
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash('Post has been updated!', 'success mt-4')
            return redirect(url_for('post', post_id=post.id))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
        return render_template('create_post.html', title='Edit Post', form=form, legend='Edit Post')
    else:
        abort(403)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author == current_user or current_user.account_type == 'Owner' or current_user.account_type == 'Administrator':
        db.session.delete(post)
        db.session.commit()
        flash('Post has been deleted!', 'success mt-4')
        return redirect(url_for('home'))
    else:
        abort(403)


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

# ===========================================
# ========== Admin-Specific Routes ==========
# ===========================================

@app.route("/register", methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated and (current_user.account_type == "Owner" or current_user.account_type == "Administrator"):
    if True:
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, full_name=form.full_name.data, password=hashed_password, account_type=form.account_type.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in.', 'success mt-4')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)
    return redirect(url_for('home'))

@app.route("/announcements")
def announcements():
    page = request.args.get('page', 1, type=int)
    posts = Announcement.query.order_by(Announcement.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('announcements.html', title='Announcements', posts=posts)

@app.route("/announcement/new", methods=['GET', 'POST'])
@login_required
def new_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(announcement)
        db.session.commit()
        flash('Announcement has been created!', 'success mt-4')
        return redirect(url_for('announcements'))
    return render_template('create_announcement.html', title='New Announcement', form=form, legend='New Announcement')

@app.route("/announcement/<int:announcement_id>/delete", methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    if current_user.account_type == 'Owner' or current_user.account_type == 'Administrator':
        db.session.delete(announcement)
        db.session.commit()
        flash('Announcement has been deleted!', 'success mt-4')
        return redirect(url_for('announcements'))
    else:
        abort(403)

@app.route("/moderate")
@login_required
def moderate():
    return render_template('moderate.html', title='Moderate')

@app.route("/delete_posts")
@login_required
def delete_posts():
    if current_user.account_type == 'Owner' or current_user.account_type == 'Administrator':
        all_posts = Post.query.all()
        for post in all_posts:
            db.session.delete(post)
        db.session.commit()
        flash('All posts have been deleted!', 'success mt-4')
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', title='Home', posts=posts)

@app.route("/reset_database")
@login_required
def reset_database():
    if current_user.account_type == 'Owner' or current_user.account_type == 'Administrator':
        all_posts = Post.query.all()
        for post in all_posts:
            db.session.delete(post)

        all_users = User.query.all()
        for user in all_users:
            db.session.delete(user)

        all_announcements = Announcement.query.all()
        for annc in all_announcements:
            db.session.delete(annc)

        db.session.commit()
        flash('Database has been reset!', 'success mt-4')
    return render_template('home.html', title='Home')

@app.route("/display_users/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    user_posts = Post.query.filter_by(user_id=user_id).all()
    if current_user.account_type == 'Owner' or current_user.account_type == 'Administrator':
        for post in user_posts:
            db.session.delete(post)
        db.session.delete(user)
        db.session.commit()

        flash('User has been deleted!', 'success mt-4')
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('home.html', title='Home', posts=posts)
    else:
        abort(403)