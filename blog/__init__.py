from flask import Flask, redirect, url_for
from blog.main.admin import admin
from blog.main.views import main_blueprint
from config import BaseConfig
from extensions import db, login_manager, oauth


def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    db.init_app(app)
    admin.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    app.register_blueprint(main_blueprint)
    from .main import views

    @app.route('/')
    def home():
        return redirect(url_for('main.index'))

    return app


app = create_app()
