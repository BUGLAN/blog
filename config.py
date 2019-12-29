import os

class BaseConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@0.0.0.0:3306/blog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'zh_CN'  # flask-admin internationlization
    SECRET_KEY = 'you-will-never-guess-me'
    UPLOAD_FOLDER =  os.path.join(os.getcwd(), 'blog', 'static', 'user')
    ALLOWED_FILE_TYPES = ['jpg', 'png', 'pdf', 'zip', 'mp4', 'rmvb', 'jpeg', 'gif', 'txt']


class TestingConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/blog_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'zh_CN'  # flask-admin internationlization
    SECRET_KEY = 'the-testing-secret-key'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'blog', 'static', 'user')
    ALLOWED_FILE_TYPES = ['jpg', 'png', 'pdf', 'zip', 'mp4', 'rmvb', 'jpeg', 'gif', 'txt']