from . import cloud_hub_blueprint
from flask import request, render_template, current_app
from blog.main.models import File
from flask_login import current_user, login_required
import os
from extensions import db, check_file_type


@cloud_hub_blueprint.route('/cloud_hub/index')
def cloud_hub_index():
    # 首页视图
    pass


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


@cloud_hub_blueprint.route('/cloud_hub/download')
def cloud_hub_download():
    pass
