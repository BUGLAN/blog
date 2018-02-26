from . import novel_blueprint
from flask import render_template, request, redirect, url_for
from .spider import Spider


@novel_blueprint.route('/novel/search')
def search():
    keyword = request.args.get('keyword')
    items = Spider.search(keyword)
    if items:
        return render_template('novel/search.html', items=items)
    elif items == "连接错误":
        return "连接错误"
    return render_template('novel/search.html')


@novel_blueprint.route('/novel/<key_url>/')
def novel_chapters(key_url):
    full_url = "http://www.biquge5200.com/" + key_url + '/'
    chapters, introduce, title = Spider.get_lists(full_url)
    return render_template('novel/novel_chapters.html', introduce=introduce, chapters=chapters, title=title)


@novel_blueprint.route('/novel/<key_url>/<key_page>')
def novel_page(key_url, key_page):
    full_url = "http://www.biquge5200.com/" + key_url + '/' + key_page
    try:
        page, title = Spider.get_page(full_url)
    except ValueError:
        return redirect(url_for('novel.novel_chapters', key_url=key_url))
    else:
        key = [key_url, key_page]
        return render_template('novel/novel_page.html', page=page, title=title, key=key)
