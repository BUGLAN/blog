from blog.main import main_blueprint
from flask import render_template, request, redirect, url_for, session, abort
from blog.main.models import User, Post, Category, Tag
from extensions import db
import datetime
import markdown
from flask_login import login_user, logout_user, login_required


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
    categories, tags = sidebar_date();
    posts = filter_markdown(posts)
    return render_template('blog/index.html', posts=posts, pagination=pagination, categories=categories, tags=tags)


@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User()
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.password = request.form.get('password1')
        user.publish_date = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('blog/register.html')


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username'), password=request.form.get('password')).first()
        user2 = User.query.filter_by(email=request.form.get('username'), password=request.form.get('password')).first()
        if user:
            # session['username'] = user.username
            login_user(user, remember=request.form.get('remember'))
            return redirect(url_for('main.index'))
        if user2:
            session['username'] = user2.username
            login_user(user2, remember=request.form.get('remember'))
            return redirect(url_for('main.index'))
        else:
            abort(404)
    return render_template('blog/login.html')


@main_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # session.pop('username', None)
    logout_user()
    return redirect(url_for('main.index'))


@main_blueprint.route('/post/<int:page>/detail')
def detail(page):
    post = Post.query.get(page)
    categories, tags = sidebar_date();
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
    pagination = Post.query.filter_by(category_id=category.id).order_by(Post.publish_date.desc()).paginate(page, 5, error_out=False)
    posts = pagination.items
    categories, tags = sidebar_date();
    posts = filter_markdown(posts)
    return render_template('blog/index.html', posts=posts, pagination_category=pagination, categories=categories, tags=tags, category_name=category.name)


@main_blueprint.route('/tag/<string:tags>/<int:page>')
def show_tag(tags, page=1):
    tag = Tag.query.filter_by(name=tags).first()
    tag_id = tag.id
    pagination =tag.posts.order_by(Post.publish_date.desc()).paginate(page, 5, error_out=False)
    posts = pagination.items
    categories, tags = sidebar_date();
    posts = filter_markdown(posts)
    return render_template('blog/index.html', posts=posts, pagination_tag=pagination, categories=categories, tags=tags, tag_name=tag.name)

