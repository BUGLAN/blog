import os

from . import cloud_hub_blueprint
from flask import request, render_template, current_app, make_response, send_from_directory
from blog.main.models import File
from flask_login import current_user, login_required
from extensions import db, check_file_type


@cloud_hub_blueprint.route('/cloud_hub/index')
def cloud_hub_index():
    # 首页视图
    return render_template('cloud_hub/cloud_hub_index.html')


@cloud_hub_blueprint.route('/cloud_hub/uploads', methods=['GET', 'POST'])
@login_required
def cloud_hub_uploads():
    # 先搞单文件上传
    if request.method == 'POST':
        file = request.files.get('file')
        # 验证file.filename
        if file and check_file_type(file.filename):
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.username)
            if not os.path.exists(path):
                os.makedirs(path)
                # 如果不存在这样的路径那么直接创键这样的目录
            user_file = File()
            user_file.name = file.filename
            user_file.path = os.path.join(path, file.filename)
            user_file.user_id = current_user.id
            db.session.add(user_file)
            db.session.commit()
            file.save(os.path.join(path, file.filename))
            return "upload success"
        return '文件不存在', 404
    return render_template('cloud_hub/cloud_hub_index.html')


def download_file(username, filename):
    # 下载工厂函数
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], username)
    full_path = os.path.join(directory, filename)
    if os.path.exists(full_path):
        res = make_response(send_from_directory(directory, filename, as_attachment=True), 200)
        # 中文的话 先编码再解码为latin-1
        res.headers["Content-Disposition"] = "attachment; filename={}".format(
           filename.encode().decode('latin-1'))
        return res
    return "文件不存在"


@cloud_hub_blueprint.route('/cloud_hub/download')
def cloud_hub_download():
    # 需要 用户名和文件名
    username = 'BUGLAN'
    filename = '小丑.jpg'
    response = download_file(username, filename)
    return response
