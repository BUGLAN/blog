from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from blog.main.models import User, Category, Post, Tag
from extensions import db
from blog.main.widgets import SimpleMDEAreaField
from flask_login import current_user
from flask import request, redirect, url_for
# from blog.main.widgets import CKTextAreaField


class PostView(ModelView):
    # 增加 专栏

    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False
    page_size = 15
    form_overrides = dict(text=SimpleMDEAreaField)
    column_searchable_list = ('text', 'title')
    column_filters = ('publish_date',)
    column_default_sort = ('publish_date', True)
    # 倒序排序
    create_template = 'admin/post_edit.html'
    edit_template = 'admin/post_edit.html'


class MyView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.username == "admin":
            return True
        return False


class MyAdminIndexView(AdminIndexView):
    # 增加这个必须要登录后才能访问，不然显示403错误
    # 但是还是不许再每一个函数前加上这么判定的  ，不然还是可以直接通过地址访问
    def is_accessible(self):
        return current_user.is_authenticated

    # 跳转
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login', next=request.url))

    # 后台首页
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


admin = Admin(
    name='BUGLAN',
    index_view=MyAdminIndexView(),
    )
admin.add_view(MyView(User, db.session, name='用户'))
admin.add_view(PostView(Post, db.session, name='文章'))
admin.add_view(MyView(Category, db.session, name='分类'))
admin.add_view(MyView(Tag, db.session, name='标签'))
