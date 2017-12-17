from extensions import db
from flask_login import AnonymousUserMixin


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128))
    qq_num = db.Column(db.String(128))
    introduction = db.Column(db.String(256))
    password = db.Column(db.String(128))
    publish_date = db.Column(db.DateTime)
    head_portrait = db.Column(db.String(256), default='user/BUGLAN/:L3.png')
    posts = db.relationship(
        'Post',
        backref='user',
        lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return str(self.id)


post_tag = db.Table(
    'post_tag',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text)
    publish_date = db.Column(db.DateTime)
    modified_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    tags = db.relationship(
        'Tag',
        secondary=post_tag,
        backref=db.backref('posts', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return '<Post {}>'.format(self.title)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    publish_date = db.Column(db.DateTime)
    modified_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts = db.relationship(
        'Post',
        backref='category',
        lazy='dynamic'
    )

    def __repr__(self):
        return '<Category {}>'.format(self.name)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    publish_date = db.Column(db.DateTime)
    modified_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


# User -> Post 一对多
# Category -> Post 一对多
# Post -> Tag 多对多
# User -> Tag 一对一