from blog.main import main_blueprint
from flask import render_template, request, redirect, url_for, session, abort, jsonify
from blog.main.models import User, Post, Category, Tag
from extensions import db, github
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
# -------------------------------------------------

@main_blueprint.route('/user/<username>')
@login_required
def user_detail(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    else:
        posts = Post.query.filter_by(user_id=user.id).order_by(Post.publish_date.desc()).all()
        return render_template('blog/user_detail.html', posts=posts)
    # return render_template('blog/user_detail.html')


@main_blueprint.route('/post/post_delete/<int:user_id>/<int:post_id>')
@login_required
def post_delete(user_id, post_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post.user_id == user.id:
         db.session.delete(post)
         db.session.commit()
         return redirect(url_for('main.user_detail', username=user.username))
    else:
        abort(404)



# @main_blueprint.route('/post/post_change/<int:user_id>/<int:post_id>', methods=['GET', 'POST'])
# @login_required
# def post_change(user_id, post_id):
#     user = User.query.filter_by(id=user_id).first_or_404()
#     post = Post.query.filter_by(id=post_id).first_or_404()
#     if post.user_id == user.id:
#         if request.method == 'POST':
#             post.title = request.form['title']
#             post.text = request.form['text']
#             db.session.add(post)
#             db.session.commit()
#             return redirect(url_for('main.user_detail', username=user.username))


@main_blueprint.route('/post/post_edit/<int:user_id>/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_edit(user_id, post_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    post = Post.query.filter_by(id=post_id).first_or_404()
    if request.method == 'POST':
        if post.user_id == user.id:
            post.title = request.form['title']
            post.text = request.form['context']
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('main.user_detail', username=user.username))

    return render_template('blog/post_edit.html', post=post)