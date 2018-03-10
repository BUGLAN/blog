# coding=utf-8
import os

from . import cloud_hub_blueprint
from flask import request, render_template, current_app, make_response, send_from_directory, abort, redirect, url_for
from flask_login import current_user, login_required
from extensions import check_file_type


def foreach(root_dir):
    """
    :param root_dir:
    :return: 将当前目录下的一级文件和一级目录遍历出来
    """
    file_dirs = {}
    for lists in os.listdir(root_dir):
        path = os.path.join(root_dir, lists)
        file_dirs[os.path.basename(path)] = {"abspath": os.path.abspath(path)}
        if os.path.isdir(path):
            foreach(path)
    return file_dirs


@cloud_hub_blueprint.route('/cloud_hub/index')
@login_required
def cloud_hub_index():
    root_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.username)
    file_dirs = foreach(root_dir)
    return render_template('cloud_hub/cloud_index.html', files=file_dirs, parent_dir=root_dir)


@cloud_hub_blueprint.route('/cloud_hub/index/path')
@login_required
def cloud_hub_folders():
    # dir get method
    path = request.values.get('path')
    if path:
        root_dir = path
        file_dirs = foreach(root_dir)
        return render_template('cloud_hub/cloud_index.html', files=file_dirs, parent_dir=root_dir)
    else:
        return redirect(url_for('cloud_hub.cloud_index'))


@cloud_hub_blueprint.route('/cloud_hub/uploads', methods=['GET', 'POST'])
@login_required
def cloud_hub_uploads():
    # 单文件上传
    if request.method == 'POST':
        file = request.files.get('file')
        path = request.values.get('path')

        if file and check_file_type(file.filename):
            if path != "null":
                pass
            else:
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.username)
            if not os.path.exists(path):
                os.makedirs(path)  # 如果不存在这样的路径那么直接创键这样的目录
            file.save(os.path.join(path, file.filename))
            return "upload success"
        return '文件不存在', 404
    return render_template('cloud_hub/cloud_hub_index.html')


@cloud_hub_blueprint.route('/cloud_hub/multiple_uploads', methods=['GET', 'POST'])
@login_required
def cloud_hub_multiple_uploads():
    if request.method == 'POST':
        files = request.files.get('file')
        return 'post request'
    return 'bad request'


def download_file(abspath):
    # 下载工厂函数
    if os.path.exists(abspath):
        res = make_response(
            send_from_directory(os.path.dirname(abspath), os.path.basename(abspath), as_attachment=True), 200)
        # 中文的话 先编码再解码为latin-1
        res.headers["Content-Disposition"] = "attachment; filename={}".format(
            os.path.basename(abspath).encode().decode('latin-1'))
        return res
    return "文件不存在"


@cloud_hub_blueprint.route('/cloud_hub/download')
@login_required
def cloud_hub_download():
    abspath = request.values.get('abspath')
    response = download_file(abspath)
    return response


@cloud_hub_blueprint.route('/cloud_hub/add_folder', methods=['POST'])
@login_required
def cloud_hub_add_folder():
    parent_dir, dir_name = request.values.get('parent_dir'), request.values.get('dir_name')
    print(parent_dir, dir_name)
    if os.path.exists(parent_dir) and not os.path.exists(dir_name):
        if not os.path.exists(os.path.join(parent_dir, dir_name)):
            os.mkdir(os.path.join(parent_dir, dir_name))
            return redirect(url_for('cloud_hub.cloud_hub_folders', path=parent_dir))
        else:
            return '文件已存在'
    return "请输入文件名"


@cloud_hub_blueprint.route('/cloud_hub/home')
def home():
    return render_template('cloud_hub/cloud_index.html')
