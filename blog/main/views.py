from blog.main import main_blueprint
from flask import render_template, request, redirect, url_for, session, abort
from blog.main.models import User, Post, Category, Tag
from extensions import db, github
import datetime
import markdown
from flask_login import login_user, logout_user, login_required, current_user


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
        user = User.query.filter_by(username=request.form.get('username'),
                                    password=request.form.get('password')).first()
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
    pagination = Post.query.filter_by(category_id=category.id).order_by(Post.publish_date.desc()).\
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
    pagination =tag.posts.order_by(Post.publish_date.desc()).paginate(page, 5, error_out=False)
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


@main_blueprint.route('/user/<username>/user_detail', methods=['GET', 'POST'])
@login_required
def user_detail(username):
    if current_user.username == username:
        return render_template('blog/user_detail.html')
# -------------------------------------------------


# adminter
@main_blueprint.route('/user/<username>/post_adminter')
@login_required
def post_adminter(username):
    if current_user.username == username:
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.publish_date.desc()).all()
        categories = Category.query.filter_by(user_id=current_user.id).all()
        tags = Tag.query.filter_by(user_id=current_user.id).all()
        # 现在要求得到用户创建的tag 获取列表
        return render_template('blog/post_adminter.html', posts=posts, categories=categories, tags=tags)
    else:
        return "您无权访问他人的主页"


@main_blueprint.route('/user/<username>/category_adminter')
@login_required
def category_adminter(username):
    if current_user.username == username:
        categories = Category.query.filter_by(user_id=current_user.id).all()
        # 现在要求得到用户创建的tag 获取列表
        return render_template('blog/category_adminter.html', categories=categories)
    else:
        return "您无权访问他人的主页"


@main_blueprint.route('/user/<username>/tag_adminter')
@login_required
def tag_adminter(username):
    if current_user.username == username:
        tags = Tag.query.filter_by(user_id=current_user.id).all()
        # 现在要求得到用户创建的tag 获取列表
        return render_template('blog/tag_adminter.html', tags=tags)
    else:
        return "您无权访问他人的主页"
# ----------


# delete
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


@main_blueprint.route('/post/<int:user_id>/<int:category_id>/categort_delete')
@login_required
def category_delete(user_id, category_id):
    if current_user.id == user_id:
        category = Category.query.filter_by(id=category_id).first_or_404()
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('main.category_adminter', username=current_user.username))
    else:
        return "没有权限"


@main_blueprint.route('/post/<int:user_id>/<int:tag_id>/tag_delete')
@login_required
def tag_delete(user_id, tag_id):
    if current_user.id == user_id:
        tag = Tag.query.filter_by(id=tag_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        return redirect(url_for('main.tag_adminter', username=current_user.username))
    else:
        return "没有权限"
# -----------


# edit
@main_blueprint.route('/post/<int:user_id>/<int:post_id>/post_edit', methods=['GET', 'POST'])
@login_required
def post_edit(user_id, post_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    post = Post.query.filter_by(id=post_id).first_or_404()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    cat = Category.query.filter_by(id=post.category_id).first()
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        if post.user_id == user.id:
            post.title = request.form['title']
            post.text = request.form['context']
            tag_s = request.values.getlist('s_option')
            # 得到Tag 的 id
            if tag_s:
                for tag_id in tag_s:
                    t = Tag.query.filter_by(id=int(tag_id)).first()
                    post.tags.append(t)
            try:
                post.category_id = Category.query.filter_by(name=request.form['category_name']).first().id
            except:
                # 解决方法将category_id 改为 category_name
               pass
            else:
                db.session.add(post)
                db.session.commit()
                return redirect(url_for('main.post_adminter', username=user.username))

    return render_template('blog/post_edit.html', post=post, categories=categories, cat=cat, tags=tags)


@main_blueprint.route('/post/<int:user_id>/<int:category_id>/category_edit', methods=['GET', 'POST'])
@login_required
def category_edit(user_id, category_id):
    if current_user.id == user_id:
        category = Category.query.filter_by(id=category_id).first_or_404()
        if request.method == 'POST':
            category.name = request.values.get('name')
            category.publish_date = request.values.get('publish_date')
            category.modified_date = request.values.get('modified_date')
            category.user_id = current_user.id
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('main.category_adminter', username=current_user.username))
        return render_template('blog/category_edit.html', category=category)

    else:
        return "没有权限"


@main_blueprint.route('/post/<int:user_id>/<int:tag_id>/tag_edit', methods=['GET', 'POST'])
@login_required
def tag_edit(user_id, tag_id):
    if current_user.id == user_id:
        tag = Tag.query.filter_by(id=tag_id).first_or_404()
        if request.method == 'POST':
            tag.name = request.values.get('name')
            tag.publish_date = request.values.get('publish_date')
            tag.modified_date = request.values.get('modified_date')
            tag.user_id = current_user.id
            db.session.add(tag)
            db.session.commit()
            return redirect(url_for('main.tag_adminter', username=current_user.username))
        return render_template('blog/tag_edit.html', tag=tag)
    else:
        return "没有权限"
# ------------


# new
@main_blueprint.route('/post/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.is_authenticated:
        categories = Category.query.all()
        tags = Tag.query.all()
        if request.method == 'POST':
            post = Post(
                title=request.values.get('title'),
                text=request.values.get('context'),
                publish_date=request.values.get('publish_date'),
                modified_date=request.values.get('modified_date'),
                user_id=current_user.id,
                # category_id=request.values.get('category_name'),
            )
            for tag_id in request.values.getlist('s_option'):
                tag = Tag.query.filter_by(id=tag_id).first()
                post.tags.append(tag)
                db.session.add(post)
            db.session.commit()
            return redirect(url_for('main.post_adminter', username=current_user.username))
    return render_template('blog/new_post.html', categories=categories,  tags=tags)


@main_blueprint.route('/post/new_category', methods=['GET', 'POST'])
@login_required
def new_category():
    if current_user.is_authenticated:
        if request.method == 'POST':
            category = Category()
            category.name = request.values.get('name')
            category.publish_date = request.values.get('publish_date')
            category.modified_date = request.values.get('modified_date')
            category.user_id = current_user.id
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('main.category_adminter', username=current_user.username))
        return render_template('blog/new_category.html')


@main_blueprint.route('/post/new_tag', methods=['GET', 'POST'])
@login_required
def new_tag():
    if current_user.is_authenticated:
        if request.method == 'POST':
            tag = Tag()
            tag.name = request.values.get('name')
            tag.publish_date = request.values.get('publish_date')
            tag.modified_date = request.values.get('modified_date')
            tag.user_id = current_user.id
            db.session.add(tag)
            db.session.commit()
            return redirect(url_for('main.tag_adminter', username=current_user.username))
        return render_template('blog/new_tag.html')

# ------------
