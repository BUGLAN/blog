import os


class BaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/blog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'zh_CN'  # flask-admin internationlization
    SECRET_KEY = 'you-will-never-guess-me'
    UPLOAD_FOLDER = os.getcwd() + '\\blog\\static\\user'
