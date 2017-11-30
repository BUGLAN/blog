from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.session_protection = 'strong'
login_manager.login_message = 'please login to access this page'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from blog.main.models import User
    return User.query.filter_by(id=user_id).first()
