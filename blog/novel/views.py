from . import novel_blueprint
from flask import render_template, request
from .spider import Spider


@novel_blueprint.route('/novel/search')
def search():
    keyword = request.args.get('keyword')
    items = Spider.search(keyword)
    if items:
        return render_template('novel/search.html', items=items)
    return render_template('novel/search.html')


@novel_blueprint.route('/novel/<key_url>/')
def novel_chapters(key_url):
    full_url = "http://www.biquge5200.com/" + key_url + '/'
    _, intro = Spider.get_lists(full_url)
    return intro
