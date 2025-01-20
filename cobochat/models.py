from cobochat import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(20), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String, nullable=False)
    bio = db.Column(db.Text)
    posts = db.relationship('Post', backref='author', lazy=True)
    announcements = db.relationship('Announcement', backref='author', lazy=True)

    def __repr__(self): # How the object is printed whenever we print it
        return f"User('{self.username}', '{self.full_name}', '{self.image_file}', '{self.account_type}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # removed a nullable=False argument to allow for deletion of users but may cause bugs idk
    post_image = db.Column(db.String(20), nullable=True)
    like_counter = db.Column(db.Integer, nullable=True)
    dislike_counter = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
    
class Likes(db.Model):
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Dislikes(db.Model):
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Announcement('{self.title}', '{self.date_posted}')"