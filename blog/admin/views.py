import os
import datetime

from blog.admin import admin_blueprint
from werkzeug.utils import secure_filename
from blog.main.views import db, login_required, current_user, request, redirect, \
    url_for, render_template, Post, User, Category, Tag, abort, current_app
from extensions import check_file_type


@admin_blueprint.route('/user/<username>/user_detail', methods=['GET', 'POST'])
@login_required
def user_detail(username):
    if current_user.username == username:
        if request.method == 'POST':
            current_user.username = request.values.get('username')
            current_user.qq_num = request.values.get('qq_num')
            current_user.email = request.values.get('email')
            current_user.introduction = request.values.get('introduction')
            current_user.modified_date = datetime.datetime.now()
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('my_admin.user_detail', username=current_user.username))
        return render_template('blog/user_detail.html')
    else:
        abort(404)


# -------------------------------------------------


# adminter
@admin_blueprint.route('/user/<username>/post_adminter')
@login_required
def post_adminter(username):
    if current_user.username == username:
        posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.publish_date.desc()).all()
        categories = Category.query.filter_by(user_id=current_user.id).all()
        tags = Tag.query.filter_by(user_id=current_user.id).all()
        # 现在要求得到用户创建的tag 获取列表
        return render_template('blog/post_adminter.html', posts=posts, categories=categories, tags=tags)
    else:
        return "您无权访问他人页面"


@admin_blueprint.route('/user/<username>/category_adminter')
@login_required
def category_adminter(username):
    if current_user.username == username:
        categories = Category.query.filter_by(user_id=current_user.id).all()
        # 现在要求得到用户创建的tag 获取列表
        return render_template('blog/category_adminter.html', categories=categories)
    else:
        abort(404)


@admin_blueprint.route('/user/<username>/tag_adminter')
@login_required
def tag_adminter(username):
    if current_user.username == username:
        tags = Tag.query.filter_by(user_id=current_user.id).all()
        # 现在要求得到用户创建的tag 获取列表
        return render_template('blog/tag_adminter.html', tags=tags)
    else:
        abort(404)


# ----------


# delete
@admin_blueprint.route('/post/post_delete/<int:user_id>/<int:post_id>')
@login_required
def post_delete(user_id, post_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    post = Post.query.filter_by(id=post_id).first_or_404()
    if post.user_id == user.id:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('my_admin.post_adminter', username=user.username))
    else:
        abort(404)


@admin_blueprint.route('/post/<int:user_id>/<int:category_id>/category_delete')
@login_required
def category_delete(user_id, category_id):
    if current_user.id == user_id:
        category = Category.query.filter_by(id=category_id).first_or_404()
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('my_admin.category_adminter', username=current_user.username))
    else:
        abort(404)


@admin_blueprint.route('/post/<int:user_id>/<int:tag_id>/tag_delete')
@login_required
def tag_delete(user_id, tag_id):
    if current_user.id == user_id:
        tag = Tag.query.filter_by(id=tag_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        return redirect(url_for('my_admin.tag_adminter', username=current_user.username))
    else:
        abort(404)


# -----------


# edit
@admin_blueprint.route('/post/<int:user_id>/<int:post_id>/post_edit', methods=['GET', 'POST'])
@login_required
def post_edit(user_id, post_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    post = Post.query.filter_by(id=post_id).first_or_404()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    cat = Category.query.filter_by(id=post.category_id).first()
    tags = Tag.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        if post.user_id == user.id:
            post.title = request.values.get('title')
            post.text = request.values.get('context')
            post.modified_date = datetime.datetime.now()
            tag_s = request.values.getlist('s_option')
            # 得到Tag 的 id
            if tag_s:
                for tag_id in tag_s:
                    t = Tag.query.filter_by(id=int(tag_id)).first()
                    post.tags.append(t)

            if request.values.get('category') == '' or None:
                db.session.add(post)
                db.session.commit()
            else:
                post.category_id = request.values.get('category')
                db.session.add(post)
                db.session.commit()
            return redirect(url_for('my_admin.post_adminter', username=user.username))

    return render_template('blog/post_edit.html', post=post, categories=categories, cat=cat, tags=tags)


@admin_blueprint.route('/post/<int:user_id>/<int:category_id>/category_edit', methods=['GET', 'POST'])
@login_required
def category_edit(user_id, category_id):
    if current_user.id == user_id:
        category = Category.query.filter_by(id=category_id).first_or_404()
        if request.method == 'POST':
            category.name = request.values.get('category_name')
            category.modified_date = datetime.datetime.now()
            category.user_id = current_user.id
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('my_admin.category_adminter', username=current_user.username))
        return render_template('blog/category_edit.html', category=category)

    else:
        abort(404)


@admin_blueprint.route('/post/<int:user_id>/<int:tag_id>/tag_edit', methods=['GET', 'POST'])
@login_required
def tag_edit(user_id, tag_id):
    if current_user.id == user_id:
        tag = Tag.query.filter_by(id=tag_id).first_or_404()
        if request.method == 'POST':
            tag.name = request.values.get('tag_name')
            tag.modified_date = datetime.datetime.now()
            tag.user_id = current_user.id
            db.session.add(tag)
            db.session.commit()
            return redirect(url_for('my_admin.tag_adminter', username=current_user.username))
        return render_template('blog/tag_edit.html', tag=tag)
    else:
        abort(404)


# ------------


# new
@admin_blueprint.route('/post/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    if current_user.is_authenticated:
        categories = Category.query.all()
        tags = Tag.query.all()
        if request.method == 'POST':
            print(request.values.get('title'))
            post = Post(
                title=request.values.get('title'),
                text=request.values.get('context'),
                publish_date=datetime.datetime.now(),
                modified_date=datetime.datetime.now(),
                user_id=current_user.id,
            )
            if request.values.get('category') and isinstance(request.values.get('category'), int):
                post.category_id = request.values.get('category')
            if request.values.getlist('s_option'):
                for tag_id in request.values.getlist('s_option'):
                    tag = Tag.query.filter_by(id=tag_id).first()
                    post.tags.append(tag)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('my_admin.post_adminter', username=current_user.username))
        return render_template('blog/new_post.html', categories=categories, tags=tags)
    else:
        abort(404)


@admin_blueprint.route('/post/new_category', methods=['GET', 'POST'])
@login_required
def new_category():
    if current_user.is_authenticated:
        if request.method == 'POST':
            category = Category()
            category.name = request.values.get('category_name')
            category.publish_date = datetime.datetime.now()
            category.modified_date = datetime.datetime.now()
            category.user_id = current_user.id
            db.session.add(category)
            db.session.commit()
            return redirect(url_for('my_admin.category_adminter', username=current_user.username))
        return render_template('blog/new_category.html')
    else:
        abort(404)


@admin_blueprint.route('/post/new_tag', methods=['GET', 'POST'])
@login_required
def new_tag():
    if current_user.is_authenticated:
        if request.method == 'POST':
            tag = Tag()
            tag.name = request.values.get('tag_name')
            tag.publish_date = datetime.datetime.now()
            tag.modified_date = datetime.datetime.now()
            tag.user_id = current_user.id
            db.session.add(tag)
            db.session.commit()
            return redirect(url_for('my_admin.tag_adminter', username=current_user.username))
        return render_template('blog/new_tag.html')
    else:
        abort(404)


# ------------


@admin_blueprint.route('/user/upload_portrait', methods=['GET', 'POST'])
@login_required
def upload_portrait():
    if current_user.is_authenticated:
        if request.method == 'POST':
            file = request.files['file']
            if file and check_file_type(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.username)
                if not os.path.exists(path):
                    os.makedirs(path)
                user = User.query.filter_by(username=current_user.username).first()
                user.head_portrait = str('user' + '/' + current_user.username + '/' + filename)
                db.session.add(user)
                db.session.commit()
                file.save(os.path.join(path, filename))
                return redirect(url_for('my_admin.user_detail', username=current_user.username))
            return '文件不存在'
        else:
            return {"error": "the way is not post or get"}
    else:
        return '您没有权限访问'
