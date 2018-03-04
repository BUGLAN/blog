from flask import Flask
# from blog.main.admin import admin
from config import BaseConfig
from extensions import db, login_manager, oauth, date_filter, null_filter, url_filter, page_filter, isdir


def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    db.init_app(app)
    # admin.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    app.add_template_filter(date_filter, 'date')
    app.add_template_filter(null_filter, 'None_filter')
    app.add_template_filter(url_filter, 'url_filter')
    app.add_template_filter(page_filter, 'page_filter')
    app.add_template_filter(isdir, 'isdir')

    from blog.main.views import main_blueprint
    app.register_blueprint(main_blueprint)

    from blog.admin.views import admin_blueprint
    app.register_blueprint(admin_blueprint)

    from blog.novel.views import novel_blueprint
    app.register_blueprint(novel_blueprint)

    from blog.cloudhub.views import cloud_hub_blueprint
    app.register_blueprint(cloud_hub_blueprint)

    from .main import views

    return app


app = create_app()
