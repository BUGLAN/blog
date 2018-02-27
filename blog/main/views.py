from blog.main import main_blueprint
from flask import render_template, request, redirect, url_for, session, abort, current_app
from blog.main.models import User, Post, Category, Tag
from extensions import db, github
import datetime
import markdown
from flask_login import login_user, logout_user, login_required, current_user
import sqlalchemy


def sidebar_date():
    categories = Category.query.all()
    tags = Tag.query.all()
    return categories, tags


def filter_markdown(posts):
    for i in range(len(posts)):
        posts[i].text = posts[i].text.replace('`', '')
        posts[i].text = posts[i].text.replace('#', '')
        posts[i].text = posts[i].text.replace('-', '')
        posts[i].text = posts[i].text.replace('>', '')
    return posts


@main_blueprint.route('/')
@main_blueprint.route('/post/<int:page>')
def index(page=1):
    pagination = Post.query.order_by(Post.publish_date.desc()).paginate(page, 5, error_out=False)
    posts = pagination.items
    categories, tags = sidebar_date()
    posts = filter_markdown(posts)
    return render_template('blog/index.html', posts=posts, pagination=pagination, categories=categories, tags=tags)


def register_filter(username, email, password1, password2):
    if len(username) < 3:
        return None
    if (len(password1) or len(password2)) < 6:
        return None
    if '@' not in email:
        return None
    if password1 != password2:
        return None
    return True


@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User()
        if not register_filter(request.form.get('username'), request.form.get('email'), request.form.get('password1'),
                               request.form.get('password2')):
            abort(403)
        try:
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            user.password = request.form.get('password')
            user.publish_date = datetime.datetime.now()
            user.modified_date = datetime.datetime.now()
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            return "密码或用户名已被他人所占用"
        else:
            login_user(user)
            return redirect(url_for('main.index'))
    return render_template('blog/register.html')


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.values.get('username')).first()
        user2 = User.query.filter_by(email=request.values.get('username')).first()
        if user is not None and user.verify_password(request.values.get('password')):
            login_user(user, remember=request.values.get('remember-me'))
            return redirect(url_for('main.index'))

        if user2 is not None and user2.verify_password(request.values.get('password')):
            login_user(user2, remember=request.values.get('remember-me'))
            return redirect(url_for('main.index'))
        else:
            abort(404)
    return render_template('blog/login.html')


@main_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main_blueprint.route('/post/<int:page>/detail')
def detail(page):
    post = Post.query.get(page)
    categories, tags = sidebar_date()
    post.text = markdown.markdown(post.text,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])
    return render_template('blog/detail.html', post=post, categories=categories, tags=tags)


@main_blueprint.route('/category/<string:categories>/<int:page>')
def show_category(categories, page=1):
    category = Category.query.filter_by(name=categories).first()
    pagination = Post.query.filter_by(category_id=category.id).order_by(Post.publish_date.desc()). \
        paginate(page, 5, error_out=False)
    posts = pagination.items
    categories, tags = sidebar_date()
    posts = filter_markdown(posts)
    return render_template('blog/index.html',
                           posts=posts,
                           pagination_category=pagination,
                           categories=categories,
                           tags=tags,
                           category_name=category.name)


@main_blueprint.route('/tag/<string:tags>/<int:page>')
def show_tag(tags, page=1):
    tag = Tag.query.filter_by(name=tags).first()
    pagination = tag.posts.order_by(Post.publish_date.desc()).paginate(page, 5, error_out=False)
    posts = pagination.items
    categories, tags = sidebar_date()
    posts = filter_markdown(posts)
    return render_template('blog/index.html',
                           posts=posts,
                           pagination_tag=pagination,
                           categories=categories, tags=tags,
                           tag_name=tag.name)


# github_login-------------------------------------
@main_blueprint.route('/github', methods=['GET', 'POST'])
def github_login():
    return github.authorize(callback=url_for('main.authorized', _external=True))


@main_blueprint.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    user = User.query.filter_by(username=me.data.get('login')).first()
    if not user:
        user = User(
            username=me.data.get('login'),
            password="123456",
            publish_date=datetime.datetime.now()
        )
        # 这里的password下次使用随机的密码
        # 邮箱貌似获取不了
        db.session.add(user)
        db.session.commit()
        login_user(user)
    else:
        login_user(user)
    return redirect(url_for('main.index'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


@main_blueprint.route('/post/archive')
@login_required
def archive():
    if current_user.is_authenticated:
        categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.publish_date.desc()).all()
        return render_template('blog/archive.html', categories=categories)
    else:
        return '您没有权限访问'
