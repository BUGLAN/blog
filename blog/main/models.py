from extensions import db
from flask_login import AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Permission:
    """
    权限表
    ADMINISTRATOR 超级管理人员 工作人员访问
    MEETER 创建会议的用户
    USER 普通用户
    """
    __tablename__ = 'permission'
    USER = 0x01
    POSTER = 0x02
    ADMINISTRATOR = 0xff


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.USER, True),
            'Admin': (Permission.POSTER | Permission.USER, False),
            'ADMINISTRATOR': (Permission.ADMINISTRATOR, False)
        }
        """
        | 按位或运算符：只要对应的二个二进位有一个为1时，结果位就为1。
        & 按位与运算符：参与运算的两个值,如果两个相应位都为1,则该位的结果为1,否则为0
        """
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" % self.name


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    qq_num = db.Column(db.String(128))
    introduction = db.Column(db.String(256))
    password = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    publish_date = db.Column(db.DateTime)
    modified_date = db.Column(db.DateTime)
    head_portrait = db.Column(db.String(256), default='user/BUGLAN/L3.png')
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), default=Permission.USER)

    # ---- 权限控制 ----
    def can(self, permission):
        return self.role and (self.role.permissions & permission) == permission

    def is_poster(self):
        """
        判断是否为会议的创建者 permissions == 3
        """
        return self.can(Permission.USER | Permission.POSTER)

    def is_admin(self):
        """
        判断是否系统管理员 permissions == 255
        """
        return self.can(Permission.ADMINISTRATOR)

    # ---- 权限控制 ----

    # ---- 登录相关 -----
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

    # ---- 登录相关 -----

    # ---- 密码哈希 ----
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        # 访问实例属性时抛出异常

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---- 密码哈希 ----

    def __repr__(self):
        return '<User {}>'.format(self.username)


post_tag = db.Table(
    'post_tag',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Post(db.Model):
    __tablename__ = 'post'

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
    __tablename__ = 'category'

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
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    publish_date = db.Column(db.DateTime)
    modified_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    link = db.Column(db.String(128))
    latest_chapter = db.Column(db.String(128))
    status = db.Column(db.String(25))
    # 本书状态
    author = db.Column(db.String(128))
    # 作者
    publish_date = db.Column(db.DateTime)
    # 创建日期
    modified_date = db.Column(db.DateTime)

    # 最后更新日期

    def __init__(self):
        super(Book, self).__init__()
        self.publish_date = datetime.now()

    def __repr__(self):
        return "<Book %r>" % self.name


# User -> Post 一对多
# Category -> Post 一对多
# Post -> Tag 多对多
# User -> Tag 一对一
