from blog import app
from blog.main.models import User, Category, Post, Tag, post_tag, Role, Book, Permission, Comment
from extensions import db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Server, Manager

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('server', Server())
manager.add_command('db', MigrateCommand)


@manager.shell
def manager_shell_context():
    return dict(app=app, db=db, User=User, Category=Category, Post=Post, Tag=Tag, post_tag=post_tag, Role=Role,
                Book=Book, Permission=Permission, Comment=Comment)


if __name__ == '__main__':
    manager.run()
