from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_oauthlib.client import OAuth


db = SQLAlchemy()
oauth = OAuth()


login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.session_protection = 'strong'
login_manager.login_message = 'please login to access this page'
login_manager.login_message_category = 'info'


# github第三方登录
github = oauth.remote_app(
    'github',
    consumer_key="a31b4764b4142a744dda",
    consumer_secret="1d75c970999542f122fc36d86db7e31b2a8a0b25",
    request_token_params={'scope': 'user:email'},
    base_url="https://api.github.com/",
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)


@login_manager.user_loader
def load_user(user_id):
    from blog.main.models import User
    return User.query.filter_by(id=user_id).first()


