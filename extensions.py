import os

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_oauthlib.client import OAuth
from datetime import datetime
from flask import current_app
from logging.handlers import RotatingFileHandler
import logging

db = SQLAlchemy()
oauth = OAuth()

login_manager = LoginManager()
login_manager.login_view = 'main.login'
# login_manager.session_protection = 'strong'
# login_manager.login_message = 'please login to access this page'
# login_manager.login_message_category = 'info'

# github第三方登录
github = oauth.remote_app(
    'github',
    consumer_key="541cf3be6df01cbe7a87",
    consumer_secret="0130a4662802a1e7467d1964d2c88022b9d7e5e2",
    request_token_params={'scope': 'user:email'},
    base_url="https://api.github.com/",
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)


# 日志配置
logger = logging.getLogger("blog_info")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('blog.log', encoding='utf8', maxBytes=10000, backupCount=1)
logging_format = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] [%(filename)s: %(funcName)s: %(lineno)s] -> "%(message)s"')
handler.setFormatter(logging_format)
logger.addHandler(handler)


# '2017-12-13 16:40:48.873676'
def date_filter(time):
    if time:
        filter_date = datetime.strftime(time, '%Y-%m-%d')
        return filter_date
    return None


def null_filter(s):
    if not s:
        return ""
    else:
        return s


def url_filter(s):
    return s.split('/')[-2]


def page_filter(s):
    return s.split('/')[-1]


def isdir(name):
    if name:
        if len(name.split('.')) == 1:
            return True
    return False


def relative_path(abspath):
    return abspath.replace(os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.username), '.')


@login_manager.user_loader
def load_user(user_id):
    from blog.main.models import User
    return User.query.filter_by(id=user_id).first()


def check_file_type(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_FILE_TYPES']
